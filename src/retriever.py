import transformer
class Retriever:
    def __init__(self):
        # You can initialize any attributes here, like database connection parameters if needed.
        pass

    def get_context(self, query):
        # data will be json in this format
        data = """{
                "metadata": {
                    "year": 2020,
                    "ticker": "MA",
                    "item": "Item 1.",
                    "description": "Business"
                },
                "content": "Mastercard is a food business, we sell breakfast cereal in Algeria"
            }
        """  
        #expected answer: according to the 2020 annual report Item 1. 
        # Business description Mastercad is a food business tht sells breakfast in Algeria

        context = (
            "Act as a financial analyst who reviews annual reports,"
            "summarizes key insights, and answers specific questions about financial "
            "metrics and company performance very concisely based on the following text: \n"
            f"{data}"
            "\n Answer without talking to the first person."
        )
        return context



        

