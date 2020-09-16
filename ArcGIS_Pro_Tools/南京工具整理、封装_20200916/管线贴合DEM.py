import arcpy
import os

arcpy.env.overwriteOutput = True


# ---------- show message in toolbox ----------

def _addMessage(mes: str) -> None:
    print(mes)
    arcpy.AddMessage(mes)
    return None


def _addWarning(mes: str) -> None:
    print(mes)
    arcpy.AddWarning(mes)
    return None


def _addError(mes: str) -> None:
    print(mes)
    arcpy.AddError(mes)
    return None


def setTempWorkspace(workspace):
    def _inner(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            # keep origin workspace
            oriWS = None
            if arcpy.env.workspace:
                oriWS = arcpy.env.workspace

            arcpy.env.workspace = workspace
            res = func(*args, **kwargs)

            try:
                if oriWS:
                    arcpy.env.workspace = oriWS
                else:
                    arcpy.ClearEnvironment("workspace")
            except:
                pass
            return res

        return _wrapper

    return _inner


def interShape3D(inDEM, inFC, outFC):


