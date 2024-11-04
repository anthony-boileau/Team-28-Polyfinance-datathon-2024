# 10K Intelligence: AI-Powered Annual Report Analysis Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9%20or%20higher-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/Powered%20by-AWS-orange?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![Claude](https://img.shields.io/badge/AI-Claude%203-pink?style=for-the-badge)](https://www.anthropic.com/)
[![SEC](https://img.shields.io/badge/Data-SEC%20EDGAR-green?style=for-the-badge)](https://www.sec.gov/edgar)
[![ChromaDB](https://img.shields.io/badge/Database-ChromaDB-red?style=for-the-badge)](https://www.trychroma.com/)

</div>

## 🏆 Team 28

| Team Member      |
| ---------------- |
| Anthony Boileau  |
| Guillaume Collin |
| Minh Huynh       |

## 🎯 Project Overview

10K Intelligence revolutionizes financial analysis by transforming complex US annual reports (SEC Form 10-K) into actionable insights through the power of generative AI. Our platform streamlines the analysis of SEC 10-K filings by providing:

- Automated document parsing and structuring
- Comprehensive historical comparisons
- In-depth technical analyses
- Natural language Q&A capabilities

Through these features, we make financial analysis more accessible and efficient for investors, analysts, and decision-makers.

### Visual Showcase

*TODO: Add GIF demonstration*
![Technical Analysis Dashboard](img/screenshot-ta.png)
![Advanced Graphing Capabilities](img/screenshot-graphs.png)

### 🌟 Key Features

#### Automated Report Parsing

Our solution offers free access to parsed textual components of 10-K forms, extracting key information from SEC EDGAR filings into a structured JSON format:

```json
{
  "ticker": "MA",
  "year": 2018,
  "items": [
    {
      "item": "Item 3.",
      "description": "Legal Proceedings",
      "content": ["ITEM 3. LEGAL PROCEEDINGS Refer to Notes 10 (Accrued Expenses and Accrued Litigation) and 18 (Legal and Regulatory Proceedings) to the consolidated financial statements included in Part II, Item 8."]
    },
    {
      "item": "Item 4.",
      "description": "Mine Safety Disclosures",
      "content": ["ITEM 4. MINE SAFETY DISCLOSURES Not applicable."]
    }
  ]
}
```

#### Advanced Analytics Suite

Our comprehensive analytics package includes:

- **Historical Analysis**: Track performance metrics across multiple years
- **Industry Benchmarking**: Compare company performance against peers
- **Interactive Q&A**: Natural language queries powered by Claude 3
- **Comprehensive Analytics**: Deep insights from financials to governance
- **Real-time Market Data**: Live market context through yfinance integration

## 🏗️ Architecture

### Technology Stack

Our platform leverages cutting-edge technologies:

- **AI Model**: Claude 3 by Anthropic, deployed on AWS
  - Chosen for its robust capabilities and free tier access (3.5 Sonnet)
  - Enables sophisticated self-prompting engineering
- **Database**: ChromaDB
  - Open-source vector database with AWS deployment support
  - Currently running locally due to AWS permission issues, however a stack was still successfully created (see [our template](./json/reference/chroma-template.json) ) through AWS and the code can be easily adapted.
  ![aws stack](img/aws-stack.png)
- **Frontend/API**: Streamlit
  - Chosen for its Python integration and development efficiency
- **Data Sources**: SEC EDGAR and yfinance
  - Selected for reliable, free access to financial data

### System Architecture

![UML Deployment Diagram](img/uml-deployment.png)
![Report Generation Flow](img/uml-sequence-generate-report.png)

## 📊 Report Components

### Financial Analysis

- Company metrics and fundamentals
- Historical performance tracking
- Industry comparisons
- KPI monitoring
- Market positioning analysis

### Leadership & Governance

- Board composition insights
- Executive leadership profiles
- Committee structure evaluation
- Compensation analysis
- DE&I metrics tracking

### Risk Assessment

- Risk factor identification and tracking
- Evolution of risk patterns
- Mitigation strategy evaluation
- Impact analysis
- Peer risk comparisons

### Market Sentiment

- News sentiment analysis
- Social media trend monitoring
- Analyst recommendation tracking
- Market perception analysis

## 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure

# Launch application
streamlit run system.py
```

## AI Explainability

Our system ensures accuracy through meticulous source tracking. Each text snippet in the vector database includes source metadata, and we prompt the LLM to provide precise citations, enhancing Claude 3's natural safeguards against hallucinations.

Example database structure:

```json
[
    {
        "metadata": {
            "year": 2020,
            "ticker": "JAMEIL",
            "item": "Item 1."
        },
        "content": "Jameil is a food business, we sell breakfast cereal in Algeria"
    },
    {
        "metadata": {
            "year": 2021,
            "ticker": "JAMEIL",
            "item": "Item 1A."
        },
        "content": "The company expanded operations to Morocco and Tunisia. Revenue grew 25% year over year."
    }
]
```

Example Q&A:

```
Q: What does Jameil sell?
A: Jameil is a food business that sells breakfast cereal. It focuses on providing affordable breakfast options to markets in North Africa, specifically Algeria (2020 annual report, Item 1).

Q: Who is Jameil's CEO?
A: The provided source does not mention the CEO of Jameil. It only states that Jameil is a food business that sells breakfast cereal in Algeria, focusing on providing affordable breakfast options to North African markets. There is no information given about the company's leadership or CEO.
```

Our vector database is optimized with approximately 32 words per vector for optimal sentence completion.

## 📈 Performance Metrics

Tested on a MacBook Air, using Python’s time module to measure query times on a random sample of 10 items:

| Metric                                     | Performance                                    |
| ------------------------------------------ | ---------------------------------------------- |
| Annual Report to JSON parsing time         | $\hat{\mu} = 3.635s, \hat{\sigma} = 1.418s$  |
| Embedding annual report to local ChromaDB  | $\hat{\mu} = 131.03s, \hat{\sigma} = 65.62s$ |
| Retrieving context and answering LLM query | $\hat{\mu} = 4.69s, \hat{\sigma} = 1.28s$    |

## 📜 License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with ❤️ during the Polyfinance 2024 Datathon*

</div>
