import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


response_model = None
response_tokenizer = None
MODEL_NAME = "bitext/Mistral-7B-Customer-Support"

def load_response_model():
    """Loads the SLM and tokenizer into memory."""
    global response_model, response_tokenizer
    if response_model is None:
        try:
            response_tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            # device_map='auto' will use GPU if available, otherwise CPU
            response_model = AutoModelForCausalLM.from_pretrained(
                MODEL_NAME,
                torch_dtype=torch.bfloat16, # Use bfloat16 for less memory usage
                device_map="auto"
            )
        except Exception as e:
            response_model = "failed"
            response_tokenizer = "failed"

def classify_email_intent(email_body: str) -> str:
    """
    Simulates a fine-tuned model to classify the intent of an email.
    """
    load_response_model()

    if response_model is None or response_model == "failed":
        return "Error: The local response model is not available. Escalating."
    
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
    
    # invalid_categories not needed maybe
    invalid_categories = [
        "escalate_shipping_delay",
        "escalate_refund_request",
        "escalate_legal_request",
        "escalate_complaint",
        "escalate_fraud_report",
        "escalate_technical_support",
        "escalate_payment_issue",
        "escalate_sales_inquiry",
        "escalate_general_inquiry",
        "escalate_sales_inquiry",
        "escalate_general_inquiry",
        "escalate_account_issue",
    ]


    # Invalid Categories:
    #     - escalate_shipping_delay: For complaints or issues regarding delayed shipments that need escalation.
    #     - escalate_legal_request: For legal inquiries, subpoenas, or requests for information from authorities.
    #     - escalate_refund_request: For refund requests that require manual approval or investigation.
    #     - escalate_fraud_report: For reports of suspected fraud, phishing, or unauthorized account activity.
    #     - escalate_complaint: For customer complaints, dissatisfaction, or negative feedback that needs human review.
    #     - escalate_technical_support: For technical issues, troubleshooting, or product malfunctions that require expert assistance.
    #     - escalate_payment_issue: For problems with payment processing, failed transactions, or billing errors.
    #     - escalate_general_inquiry: For any email that does not fit into the other categories.
    #     - escalate_sales_inquiry: For questions about price, cost, purchasing, or buying a product.
    #     - escalate_account_issue: For issues related to user accounts, passwords, login, or personal information.

    system_prompt = f"""
    You are an expert email classification agent. Your task is to read the user's email and classify it into one of the following predefined categories.
    Do not respond with anything other than the category name itself.

    Valid Categories:
        - auto_respondable_return_policy: For questions about returns, refunds, or exchanges.
        - auto_respondable_product_question: For general questions about how a product works, its features, or capabilities.
        - auto_respondable_shipping_status: For inquiries about the status or tracking of an order shipment.
        - auto_respondable_order_cancellation: For requests to cancel an order before it is shipped.
        - auto_respondable_warranty_information: For questions about product warranties, coverage, or claims.
        - auto_respondable_store_hours: For questions about store opening times, holiday hours, or location information.
        - auto_respondable_discount_inquiry: For questions about current promotions, discounts, or coupon codes.
        - auto_respondable_loyalty_program: For questions about loyalty or rewards programs, points, or membership benefits.
        - auto_respondable_subscription_management: For requests to start, stop, or modify a subscription service.
        - auto_respondable_account_update: For requests to update account information, such as address or contact details.
        - auto_respondable_feedback_acknowledgement: For acknowledging receipt of customer feedback, suggestions, or praise.
    
    Categories:
    {', '.join(valid_categories)}

    User's Email:
    "{email_body}"

    Return only the single, most appropriate category name and nothing else.
    """

    try:
        # tokenize the prompt
        inputs = response_tokenizer(system_prompt, return_tensors="pt").to(response_model.device)

        # generate the response
        outputs = response_model.generate(
            **inputs,
            max_new_tokens=16,
            temperature=0.0,
            do_sample=False,
            pad_token_id=response_tokenizer.eos_token_id
        )

        # decode the output
        full_response = response_tokenizer.decode(outputs[0], skip_special_tokens=True)

        # extract last line or first valid category from the the output
        for category in valid_categories:
            if category in full_response:
                print(f"The agent will provide the response ")
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
    load_response_model()

    if response_model is None or response_model == "failed":
        return "The agent is not responding. Escalating."
    
    # for mistral testing
    prompt = f"""<s>[INST] You are a helpful customer support agent. Your task is to write a clear and concise email response to a customer's question.
    Use the provided "Knowledge Base Context" to answer the "Customer's Email".
    If the context does not contain the answer, politely state that you could not find the information.
    Do not make up information.

    **Knowledge Base Context:**
    {knowledge_base_context}

    **Customer's Email:**
    {original_email_body}
    [/INST]
    """

    try:
        # Tokenize the input prompt
        inputs = response_tokenizer(prompt, return_tensors="pt").to(response_model.device)

        # Generate the response
        outputs = response_model.generate(
            **inputs,
            max_new_tokens=256,  # Limit the length of the reply
            temperature=0.7,
            do_sample=True,
            pad_token_id=response_tokenizer.eos_token_id
        )
        # Decode the generated tokens into text, skipping the prompt
        full_response = response_tokenizer.decode(outputs[0], skip_special_tokens=True)
        # The response includes the prompt, so we need to remove it.
        response_only = full_response.split("[/INST]")[1].strip()
        
        return response_only
    
    except Exception as e:
        print(f"Error while writing the response: {e}")
        return "Error: Agent could not generate a response. Escalating."


