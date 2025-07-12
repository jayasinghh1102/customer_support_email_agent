import os
from .slm_integration import SLM_Manager

slm_base = os.environ.get("LOCAL_SLM_PATH")
finetune_folder = os.environ.get("FINETUNE_SLM_PATH")

slm_handler = SLM_Manager()
slm_handler.load_slm(local_base_model_path=slm_base, trained_checkpoint_location=finetune_folder)

def classify_email_intent(email_body: str) -> str:
    """
    Simulates a fine-tuned model to classify the intent of an email.
    """
    
    valid_categories = [
        "auto_respondable_return_policy",
        "auto_respondable_product_question",
        "auto_respondable_shipping_status",
        "auto_respondable_order_cancellation",
        "auto_respondable_warranty_information",
        "auto_respondable_store_hours",
        "auto_respondable_discount_inquiry",
        "auto_respondable_loyalty_program",
        "auto_respondable_subscription_management",
        "auto_respondable_account_update",
        "auto_respondable_feedback_acknowledgement",
    ]
    

    system_prompt = f"""
    You are an expert email classification agent. Your task is to read the user's email and classify it into one of the following predefined categories.
    Do not respond with anything other than the category name itself.

    Categories:
    {', '.join(valid_categories)}

    User's Email:
    "{email_body}"

    Return only the single, most appropriate category name and nothing else.
    """

    user_query = email_body

    try:
        # Call new inference function
        predicted_category = slm_handler.infer_slm(system_prompt=system_prompt, user_query=user_query)

        #Check if the model's output is a valid category
        for category in valid_categories:
            if category in predicted_category:
                print(f"The agent classified the intent as: {category}")
                return category
            
        # if not found, redirect to human
        print(f"Warning: This is not return a valid category for the agent. Defaulting to escalation.")
        return "escalate_general_inquiry"
    
    except Exception as e:
        print(f"Error during fetching classification: {e}")
        return "escalate_general_inquiry"
        

def draft_response(original_email_body: str, knowledge_base_context: str) -> str:
    """
    Simulates a fine-tuned model to draft an email response.
    """
    
    system_prompt = f"""You are a helpful customer support agent. Your task is to write a clear and concise email response to a customer's question.
    Use the provided "Knowledge Base Context" to answer the customer email. If the context does not contain the answer, politely state that you could not find the information.
    Do not make up information. Limit your answer to less than 150 words. Give a paragraph output, not steps.

    **Knowledge Base Context:**
    {knowledge_base_context}
    """

    user_query = original_email_body

    try:
        # Call inference function with prepared prompts
        response = slm_handler.infer_slm(system_prompt=system_prompt, user_query=user_query)
        return response
    
    except Exception as e:
        print(f"Error while writing the response: {e}")
        return "Error: Agent could not generate a response. Escalating."


