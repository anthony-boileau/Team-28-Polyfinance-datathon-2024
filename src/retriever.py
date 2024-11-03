import transformer
class Retriever:
    def __init__(self):
        # You can initialize any attributes here, like database connection parameters if needed.
        pass

    def get_context(self, query):
        # Replace this with the actual logic to retrieve data from the database
        data = ''  # Get data from DB based on the query

        context = (
            "Act as a financial analyst who quickly reviews annual reports, "
            "summarizes key insights, and answers specific questions about financial "
            "metrics and company performance based on the following text: \n"
            f"{data}"
            "\n"
        )
        return context



        

