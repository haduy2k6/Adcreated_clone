from loginDB import MyDatabase

class myResponsitory:
    def __init__(self):
        self.collection= MyDatabase().collection()
    
    async def addNewPerson(self,**args):
        pass
    async def updateInfo(self,**args):
        pass
    async def updateRole(self,**args):
        pass
    async def updatePass(self,**args):
        pass
    async def getPass(self,**args):
        pass
    async def getInfo(self,**args):
        pass
    async def deletePerson(self,**args):
        pass