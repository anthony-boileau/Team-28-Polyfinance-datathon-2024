# Team 28 Datathon
- Anthony Boileau
- Guillaume Collin
- Minh Huynh

## Project Description:
Automatic annual report parser, historical comparer and Q&A enabled. Powered by AWS

### Technologies used
- AWS Bedrock agent with Claude 3 as Transformer
- SEC EDGAR api as source of company annual report
- Yfinance api as source of financial information
- x as Parser
- y as Vector DB
- ChatGPT and Claude as AI code assistant

## UML diagrams
![UML deployment diagram](img/uml-deployment.png)
![generate report](img/uml-sequence-generate-report.png)

## Components of the report
Each of the components are generated on a separate execution loop on the report generation UML. They are as follow:
- Basic Company Information
- Yfinance 
    - Graphs
    - KPI
    - Comparison with industry
- Leadership
    - BOD
    - History
    - High level executives
    - Commitees
    - Salary
    - DEI !nice to have
    - Governance
- Risk
    - Evolution of risk 
    - Risk mitigation strategies
- Sentiment Analysis !nice to have
    - news coverage
    - social media
    - other analysts
