def get_context(query):

    data = '' #get data from db

    context = "Act as a financial analyst who quickly reviews annual reports, summarizes key insights, and answers specific questions about financial metrics and company performance based on the following text: \n{data}"
    return context