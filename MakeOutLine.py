# !python2.7
# -*- coding: utf-8 -*-
# �ｿｽR�ｿｽ[�ｿｽf�ｿｽB�ｿｽ�ｿｽ�ｿｽO: utf-8
# ------------------------------------------------------------------------------
from __future__ import absolute_import, division, generators, print_function, unicode_literals
from future_builtins import *
import maya.cmds as cmds
import maya.mel as mel

# main func
def makeOutline():
    _fullPathList = []
    _selectedList = cmds.ls(sl=True, long=True)
    _subList = cmds.ls("*_Outline", "*Base", "eyes", sl=True, long=True)
    _objectList = list(set(_selectedList) - set(_subList))
    _surfaceShader = "outline_m"
    _displayLayer = "OL"
    _groupName = "outline_GP"

    # if no groups exist
    if not cmds.ls(_groupName, long=True):
        mel.eval('print ("[ {} ] group not found\\n");'.format(_groupName))
        return 

    if not _objectList:
        mel.eval('print ("Outline not needed\\n");')
        return

    for _object in _objectList:
        _tmpList = _object.split('|')
        _rootName = _tmpList[1]
        _mainName = _tmpList[-1]
        
        # find relatives
        if not cmds.listRelatives(_object, s=True, ni=True, f=True, type="mesh"):
            continue

        # 1. If something has outline go to the top
        if cmds.objExists(_rootName + '|' + _groupName + '|' + _mainName + '_Outline'):
            continue
        
        if cmds.objExists(_rootName + '|' + _groupName + '|' + _mainName + 'Base'):
            continue

        #New process
        _duplicate = cmds.duplicate(_object, rr=True)[0]
        _duplicate = cmds.rename(_duplicate, _mainName + '_Outline')
        
        # full path to get parents for unique objects
        cmds.parent(_duplicate, _rootName + '|' + _groupName)
        _fullPath = cmds.ls(sl=True, long=True)[0]
        _fullPathList.append(_fullPath)
        
        # Reverse normals
        mel.eval('ReversePolygonNormals;')
        # you have to do this in forloop because you cant remove multiple checks at once 
        cmds.setAttr(_fullPath + ".doubleSided", 0)
        
        # 3. move object a little inwards
        cmds.select(_fullPath, r=True)
        mel.eval('MovePolygonComponent;')
        cmds.setAttr(cmds.ls(type="polyMoveVertex")[-1] + ".localTranslateZ", -0.1)

        # 5. Delete History
        cmds.select(_fullPath, r=True)
        mel.eval('DeleteHistory;')

        # 6. outline wrap on original model
        _grpPath = _object.rsplit("|", 1)[0]
        _beforeList = cmds.ls(_grpPath, dag=True, tr=True)

        cmds.select(_object, add=True)
        mel.eval('CreateWrap;')
        
        #rename base and put it into outline group
        _afterList = cmds.ls(_grpPath, dag=True, tr=True)
        _afterList = list(set(_afterList) - set(_beforeList))
        cmds.parent(_afterList, _rootName + '|' + _groupName)
        cmds.rename(_afterList[0], _mainName + 'Base')
    
    # 4. Create and assign material
    if len(cmds.ls(_surfaceShader, type="surfaceShader")) <= 0:
        mel.eval('createRenderNodeCB -asShader "surfaceShader" surfaceShader "";')
        _surfaceShader = cmds.rename("outline_m")
        cmds.setAttr(_surfaceShader + ".outColor", 0.1882, 0.0784, 0, type="double3")
    
    cmds.select(_fullPathList, r=True)
    cmds.hyperShade(assign=_surfaceShader)

    # 7. Make layer and then rename to "OL", Lock
    cmds.select(_fullPathList, r=True)
    if len(cmds.ls(_displayLayer, type="displayLayer")) <= 0:
        cmds.createDisplayLayer(name=_displayLayer, number=1, nr=True)
    else:
        cmds.editDisplayLayerMembers(_displayLayer, _fullPathList)
    cmds.setAttr(_displayLayer + ".displayType", 2)

    
    if not _fullPathList:
        mel.eval('print ("Outline not needed\\n");')
        return

    # to tell tool user that processing has ended
    _printMessage = "{} objects made with outlines\\n".format(len(_fullPathList))
    mel.eval('print (" '+ _printMessage +' ");')
    return

makeOutline()
