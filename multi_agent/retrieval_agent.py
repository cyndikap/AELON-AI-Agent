# ce code dit: lors de la question de l'utilkisateur, cherche dans la data et affiche le resultat

class RetrievalAgent:

    def _init_(self,data):
        self.data = data

        def search(self, query):
            result =[]

            for row in self.data :
                if query.lower() in row ["text"]:
                    result.append(row)
            return result