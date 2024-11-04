# 10K Intelligence: AI-Powered Annual Report Analysis Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.9%20or%20higher-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![AWS](https://img.shields.io/badge/Powered%20by-AWS-orange?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com/)
[![Claude](https://img.shields.io/badge/AI-Claude%203-pink?style=for-the-badge)](https://www.anthropic.com/)
[![SEC](https://img.shields.io/badge/Data-SEC%20EDGAR-green?style=for-the-badge)](https://www.sec.gov/edgar)

</div>

## 🏆 Team 28

| Team Member      |
| ---------------- |
| Anthony Boileau  |
| Guillaume Collin |
| Minh Huynh       |

## 🎯 Project Overview

10K Intelligence revolutionizes financial analysis by transforming complex US annual reports (SEC Form 10-K) into actionable insights through the power of generative AI. Our solution streamlines the analysis of SEC 10-K filings by:

- Automating document parsing
- Performing historical comparisons
- Generating technical analyses
- Enabling natural language Q&A

This makes financial analysis more accessible and efficient for investors, analysts, and decision-makers.

### Screenshots

TODO: add gif
![technical-analysis](img/screenshot-ta.png)
![graphing-capability](img/screenshot-graphs.png)

### 🌟 Key Features

#### Automated Report Parsing

Extract key information from SEC EDGAR filings into structured JSON format, with section-by-section parsing capabilities. Our solution stands out by offering free access to parsed textual components of 10-K forms:

```json
{
  "ticker": "MA",
  "year": 2018,
  "items": [
    {
      ...
      "item": "Item 3.",
      "description": "Legal Proceedings",
      "content": ["ITEM 3. LEGAL PROCEEDINGS Refer to Notes 10 (Accrued Expenses and Accrued Litigation) and 18 (Legal and Regulatory Proceedings) to the consolidated financial statements included in Part II, Item 8.",
      ...
      ]
    },
    {
      "item": "Item 4.",
      "description": "Mine Safety Disclosures",
      "content":[ "ITEM 4. MINE SAFETY DISCLOSURES Not applicable."]
    }
    ...
  ]
}
```

#### Advanced Analytics Suite

- **Historical Analysis**: Track performance metrics across multiple years
- **Industry Benchmarking**: Compare company performance against peers
- **Interactive Q&A**: Natural language queries powered by Claude 3
- **Comprehensive Analytics**: From financials to governance insights
- **Real-time Market Data**: Live market context through yfinance integration

## 🏗️ Architecture

### Technology Stack

- Transformer: anthropic claude 3 on AWS. one of the models that was available. chosen because 3.5 sonnet is available up to a certain token limit for free thus unlocking the ability for claude to prompt engineer itself
- DB:  Chromadb, open source and deployable with aws. We managed to create an aws stack but then aws refused to connect no matter what we did therefore we are forced to run it locally for the data layer. it is what it is.
- UI/api layer: Streamlit, python power and ease of use
- Data sources: SEC's edgar, yfinance due to being free access

### System Architecture

![UML deployment diagram](img/uml-deployment.png)
![generate report](img/uml-sequence-generate-report.png)

## 📊 Report Components

### Financial Analysis

- Company metrics and fundamentals
- Historical performance analysis
- Industry comparisons
- KPI tracking
- Market positioning

### Leadership & Governance

- Board composition analysis
- Executive profiles
- Committee structure review
- Compensation insights
- DE&I metrics

### Risk Assessment

- Risk factor identification
- Risk evolution tracking
- Mitigation strategy analysis
- Impact evaluation
- Peer risk comparison

### Market Sentiment

- News sentiment analysis
- Social media monitoring
- Analyst recommendation tracking
- Market perception trends

## 🚀 Getting Started

```bash
# Install dependencies
pip install -r requirements.txt

# Set up AWS credentials
aws configure

# Launch application
streamlit run system.py
```

## AI Explainability

Our system prioritizes accuracy through meticulous source tracking. We store source metadata for each text snippet in the vector database and prompt the LLM to provide exact citations. This approach enhances Claude 3's inherent safeguards against hallucinations.

Example database entry:

```json
'''[
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
        ]'''
```
```
Sample LLM prompt: What does Jameil sell?

Sample LLM output: Jameil is a food business that sells breakfast cereal. It focuses on providing affordable breakfast options to markets in North Africa, specifically Algeria (2020 annual report, Item 1).

Sample LLM prompt: Who is Jameil's CEO?

Sample LLM output: The provided source does not mention the CEO of Jameil. It only states that Jameil is a food business that sells breakfast cereal in Algeria, focusing on providing affordable breakfast options to North African markets. There is no information given about the company's leadership or CEO.
```

Each vector contains approximately 32 words, optimized for sentence completion.

## 📈 Performance Metrics

Measured on a MacBook Air

| Metric                                                  | Performance                                    |
| ------------------------------------------------------- | ---------------------------------------------- |
| Annual Report to json parsing time                    | $\hat{\mu} = 3.635s, \hat{\sigma} = 1.418s$  |
| Embedding annual report to a local instance of ChromaDB | $\hat{\mu} = 131.03s, \hat{\sigma} = 65.62s$ |
|                                                         |                                                |

## 📜 License

This project is licensed under the GPL License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

*Built with ❤️ during the Polyfinance 2024 Datathon*

</div>
