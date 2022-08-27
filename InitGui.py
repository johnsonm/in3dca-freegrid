# Based on documentation at https://www.freecadweb.org/wiki/Workbench_creation


class FreegridWorkbench (Workbench):

    MenuText = "Freegrid"
    ToolTip = "A workbench for generating Freegrid system elements"
    # Ask for an icon...
    #Icon = """paste here the contents of a 16x16 xpm icon"""

    def Initialize(self):
        """This function is executed when the workbench is first activated.
        It is executed once in a FreeCAD session followed by the Activated function.
        """
        import Freegrid
        self.list = ["Freegrid"]
        self.appendToolbar("Freegrid", self.list)
        self.appendMenu("Freegrid", self.list)

    def Activated(self):
        """This function is executed when the workbench is activated"""
        return

    def Deactivated(self):
        """This function is executed when the workbench is deactivated"""
        return

    def ContextMenu(self, recipient):
        """This is executed whenever the user right-clicks on screen"""
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu("Freegrid",self.list) # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        # This is not a template, the returned string should be exactly "Gui::PythonWorkbench"
        return "Gui::PythonWorkbench"

Gui.addWorkbench(FreegridWorkbench())
