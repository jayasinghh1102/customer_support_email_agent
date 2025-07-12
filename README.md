# Customer Support Email Agent

A modular, retrieval-augmented AI agent that automatically processes customer support emails. This system connects to an email inbox, classifies incoming messages using a fine-tuned local language model, retrieves relevant information from a knowledge base (including PDFs), and uses Retrieval-Augmented Generation (RAG) to draft accurate, context-aware responses. If the query cannot be handled automatically, the agent escalates it to a human operator.

## 🚀 Features

- **Email Integration**: Connects to IMAP/SMTP email accounts
- **Intelligent Classification**: Uses a fine-tuned local LLM to classify email intent
- **RAG-Powered Responses**: Combines retrieved knowledge base context with model generation
- **Multi-Format Knowledge Base**: Supports both `.txt` and `.pdf` files
- **Smart Escalation**: Automatically replies to common queries or escalates complex issues
- **Modular Architecture**: Easily extensible for new categories or workflows
- **Secure Configuration**: Sensitive credentials managed via environment variables

## 📋 Prerequisites

- Python 3.8 or higher
- Git
- Email account with IMAP/SMTP access
- HuggingFace account (for model access)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Customer_Support_Email_Agent
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp example.env .env
   ```
   Edit `.env` with your configuration (see Configuration section below).

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Email Configuration
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_app_password
IMAP_SERVER=imap.gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Knowledge Base
KNOWLEDGE_BASE_DIR=knowledge_base

# Agent Settings
CHECK_INTERVAL_SECONDS=30

# Model Paths (Optional)
LOCAL_SLM_PATH=
FINETUNE_SLM_PATH=
```

### Email Setup

For Gmail users:
1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in your `.env` file

For other providers, check their IMAP/SMTP settings.

### Knowledge Base Setup

1. Place your knowledge base files in the `knowledge_base/` directory
2. Supported formats: `.txt` and `.pdf`
3. The system will automatically load and index these files

## 🚀 Usage

### Running the Agent

```bash
python src/main.py
```

The agent will:
1. Connect to your email inbox
2. Check for emails with subject "Test Customer Support Email"
3. Classify each email's intent
4. Either auto-respond or escalate based on classification

### Testing

1. Send an email to your configured inbox with subject: `Test Customer Support Email`
2. Include a message body that matches one of the supported categories
3. Watch the console output for processing logs

## 📁 Project Structure

```
Customer_Support_Email_Agent/
├── src/
│   ├── main.py              # Main application entry point
│   ├── agent.py             # Agent graph and workflow logic
│   ├── config.py            # Configuration management
│   ├── email_client.py      # Email connection and operations
│   ├── knowledge_base.py    # Knowledge base setup and management
│   ├── llm_integration.py   # LLM integration and response generation
│   └── slm_integration.py   # Local model integration
├── knowledge_base/          # Knowledge base files (.txt, .pdf)
├── venv/                   # Virtual environment
├── requirements.txt         # Python dependencies
├── example.env             # Environment variables template
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔧 Technical Details

### Email Classification Categories

**Auto-Respondable Categories:**
- `auto_respondable_return_policy`: Returns, refunds, exchanges
- `auto_respondable_product_question`: Product features and capabilities
- `auto_respondable_shipping_status`: Order tracking and shipping
- `auto_respondable_order_cancellation`: Order cancellation requests
- `auto_respondable_warranty_information`: Warranty and coverage
- `auto_respondable_store_hours`: Store hours and location
- `auto_respondable_discount_inquiry`: Promotions and discounts
- `auto_respondable_loyalty_program`: Rewards and membership
- `auto_respondable_subscription_management`: Subscription changes
- `auto_respondable_account_update`: Account information updates
- `auto_respondable_feedback_acknowledgement`: Feedback and suggestions

**Escalation Categories:**
- `escalate_shipping_delay`: Delayed shipment complaints
- `escalate_refund_request`: Refund requests requiring approval
- `escalate_legal_request`: Legal inquiries and subpoenas
- `escalate_complaint`: Customer complaints and dissatisfaction
- `escalate_fraud_report`: Fraud and security reports
- `escalate_technical_support`: Technical issues requiring expertise
- `escalate_payment_issue`: Payment processing problems
- `escalate_sales_inquiry`: Sales and pricing questions
- `escalate_general_inquiry`: General inquiries
- `escalate_account_issue`: Account access and security issues

### Architecture

The system uses a modular architecture with the following components:

1. **Email Client** (`email_client.py`): Handles IMAP/SMTP connections
2. **Agent Graph** (`agent.py`): Orchestrates the workflow using LangGraph
3. **LLM Integration** (`llm_integration.py`): Manages local model loading and inference
4. **Knowledge Base** (`knowledge_base.py`): Sets up vector store for RAG
5. **Configuration** (`config.py`): Manages environment variables and validation

### Workflow

1. **Email Fetching**: Connects to inbox and fetches unread emails
2. **Classification**: Uses local LLM to classify email intent
3. **Decision**: Routes to auto-response or escalation based on classification
4. **Knowledge Retrieval**: For auto-responses, retrieves relevant context
5. **Response Generation**: Uses RAG to generate context-aware responses
6. **Action**: Sends response or logs escalation

## 🔍 Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure you have internet connection for first-time model download
   - Check HuggingFace access for the model
   - Verify sufficient RAM/GPU resources

2. **Email Connection Issues**
   - Verify IMAP/SMTP settings
   - Check email credentials
   - For Gmail, ensure App Password is used

3. **Knowledge Base Issues**
   - Ensure files are in `knowledge_base/` directory
   - Check file formats (`.txt` or `.pdf`)
   - Verify file permissions

4. **Environment Variables**
   - Ensure `.env` file is in project root
   - Check variable names match `config.py`
   - Remove quotes from `.env` values

### Debug Mode

Add debug prints to see detailed processing:
```python
# In src/main.py, add more print statements
print(f"Processing email: {email_subject}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) and [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [HuggingFace Transformers](https://huggingface.co/) for local model inference
- Knowledge base powered by [Chroma](https://www.trychroma.com/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Open an issue on GitHub with detailed error information

---

**Note**: This is a private repository. Ensure no sensitive information is committed to version control.
