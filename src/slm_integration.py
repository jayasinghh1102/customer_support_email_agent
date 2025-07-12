import torch
import torch.distributed as dist
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os
import glob
from transformers import pipeline
import gc

class SLM_Manager():

    def __init__(self):

        self.model = None
        self.tokenizer = None
        self.pipe = None

    def load_slm(self, local_base_model_path: str, trained_checkpoint_location: str):

        # Quantization
        bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=False,
        )

        #Load Model
        base_model = AutoModelForCausalLM.from_pretrained(local_base_model_path,
                                                    torch_dtype=torch.bfloat16,
                                                    device_map="cuda:0",
                                                    quantization_config=bnb_config,
                                                    )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(local_base_model_path)

        # Find all directories matching the 'checkpoint-*' pattern
        checkpoint_dirs = glob.glob(os.path.join(trained_checkpoint_location, "checkpoint-*"))
        if not checkpoint_dirs:
            raise ValueError(f"No checkpoint directories found in '{trained_checkpoint_location}'")

        # Get the most recently modified checkpoint directory
        latest_checkpoint_path = max(checkpoint_dirs, key=os.path.getmtime)

        self.model = PeftModel.from_pretrained(base_model, latest_checkpoint_path)
        self.model.eval()

        self.pipe = pipeline(
        task="text-generation",
        model=self.model,
        tokenizer=self.tokenizer,
        max_length=10000,
        max_new_tokens=200,
        temperature = 0.5,
        )

    def infer_slm(self, system_prompt: str, user_query: str) -> str:
        
        if self.model is None or self.tokenizer is None:
            return "Error: Model is not loaded. Please call 'load_model_into_memory()' first"

        # Format message
        message = [
            {"role": "system", "content": user_query},
            {"role": "user", "content": system_prompt}
        ]
        prompt = self.tokenizer.apply_chat_template(message, tokenize=False, add_generation_prompt=True)

        # Get response from SLM
        result = self.pipe(prompt)
        raw_text = result[0]['generated_text']
        clean_output = self.clean_model_output(raw_output=raw_text)

        return clean_output

    def clean_model_output(self, raw_output: str) -> str:

        # Removes the instruction block from the raw model output.

        # Define the delimiter that separates the prompt from the response
        delimiter = "[/INST]"
        
        # Check if the delimiter is in the string
        if delimiter in raw_output:
            # Split the string by the delimiter and take the second part
            cleaned_text = raw_output.split(delimiter, 1)[1]
        else:
            # If the delimiter isn't found, assume the output is already clean
            cleaned_text = raw_output
            
        # Remove any leading/trailing whitespace and return
        return cleaned_text.strip()

    def unload_slm(self):
        
        if 'self.model' in locals():
            if self.model is not None:
                print("Unloading model and clearing GPU cache...")
                del self.model
                del self.tokenizer
                del self.pipe
                model = None
                tokenizer = None
                print("Model unloaded and memory freed.")
            else:
                print("No model is currently loaded.")

        gc.collect()
        torch.cuda.empty_cache()
        # Only destroy the process group if it has been initialized.
        if dist.is_initialized():
            dist.destroy_process_group()