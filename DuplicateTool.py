# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, generators, print_function, unicode_literals
from future_builtins import *
import maya.cmds as cmds
import maya.mel as mel
""" 
-----------------------------
Duplicate Mesh Align
-----------------------------
2019/12/10
------------------------
Update history:
------------------------

- Confirm exactly what to do
- Ask the guy who asked for the tool to be made if he wants the origin 
    position to be away from the object

Todo:
- Program Design
- Make the window and comment out the things to do in order
- Convert to python
- make checkbox so that the first and last aligned objects aren't overlapping, 
    ON  - if they are have atleast three 
    OFF - if they aren't have atleast one in the middle
- Find ARKW meanings
- optionVar remembers input value for the menus

ASK:
    - what is ARKW_get_optionVar line <130

Design:
Actually took 1.5 hours without checkbox and testing
1. Make UI Function
    1 Window already exists  5
    2 Window Size  5
    3 Window Layout．columnLayout, rowLayout 20
    4 CheckBox 15
    5 Done 5
    6 Send startpos and endpos values 15
    7 Send number of items 15

2. Execute Function
    1 selection is empty or not   20
    2 get startpos and end pos  30
    3 line 38,39 what's going on? - Split names 20
    4 // line 50 - is where you calculate the positioning of the 
        objects(atleast two in the old code)    20
    5 Duplicate and Rename  15
    6 Set position of the first object and last object if check box is true    10
    7 if unchecked set them with the remaining  10
    8 calculate remaining 15
"""


def CRMOD_DMA_run():
    tmpList = []
    selectList = []
    selectList = cmds.ls(sl=True, l=True)
    selectName = ""
    startPosition = cmds.floatFieldGrp("CRMOD_DMA_strPos_FFldGrp", q=True, v=True)
    endPosition = cmds.floatFieldGrp("CRMOD_DMA_endPos_FFldGrp", q=True, v=True)    
    addPosition = []
    differencePos = []
    copyName = ""
    placeFirst = cmds.checkBox("placeFirst", query=True, value = True)
    placeLast = cmds.checkBox("placeLast", query=True, value = True)

    print("PF: {}".format(placeFirst))
    print("PL: {}".format(placeLast))

    # getting the number of objects from 
    numObj = cmds.intField("CRMOD_DMA_DupNum_IFld", q=True, v=True)
    div = numObj - 1

    # calculate divisions
    div += int(not placeFirst) 
    div += int(not placeLast) 

    print("fdiv {}".format(div))
    # get a list of selection and check if only one is selected
    if len(selectList) is not 1:
        print("メッシュモデルorメッシュモデルを子に持つグループをひとつだけ選択してください！")
        return

    # get a name of selection and check if only one is selected
    tmpList = cmds.ls(sl=True, dag=True, ni=True, type="mesh")
    if len(tmpList) <= 0:
        print("メッシュモデルorメッシュモデルを子に持つグループをひとつだけ選択してください")       
        return

    tmpList = selectList[0].split('|')
    selectName = tmpList[len(tmpList)-1]

    # 移動値取得 - the value of moving each object
    for iXyz in range(3):
        differencePos.append((endPosition[iXyz] - startPosition[iXyz]))
        addPosition.append(differencePos[iXyz] / (div))

    iterRange = range(numObj)

    print("sdiv {}".format(div))
    # duplicate and rename
    for i in iterRange:

        print("iterRngBig {}".format(i))
    
        tmpList = cmds.duplicate(selectList[0], rr=True)
        
        if i < 10:
            copyName = cmds.rename(tmpList[0], (selectName + "_0" + str(i)))
        else:
            copyName = cmds.rename(tmpList[0], (selectName + "_" + str(i)))

        # set position values for first object and skip from the remaining calculation
        if i == 0 and placeFirst == True:
            cmds.setAttr((copyName + ".tx"), startPosition[0])
            cmds.setAttr((copyName + ".ty"), startPosition[1])
            cmds.setAttr((copyName + ".tz"), startPosition[2])
            continue
        
        # set position values for last object and skip from the remaining calculation
        if i == div and  placeLast == True:
            cmds.setAttr((copyName + ".tx"), endPosition[0])
            cmds.setAttr((copyName + ".ty"), endPosition[1])
            cmds.setAttr((copyName + ".tz"), endPosition[2])
            continue

        # set attributes of the remaining objects
        newPosition = addPosition[0] * (i)
        newPosition += startPosition[0]
        cmds.setAttr((copyName + ".tx"), newPosition)

        newPosition = addPosition[1] * (i)
        newPosition += startPosition[1]
        cmds.setAttr((copyName + ".ty"), newPosition)
        
        newPosition = addPosition[2] * (i)
        newPosition += startPosition[2]
        cmds.setAttr((copyName + ".tz"), newPosition)

# convert
def changeLinearUnitList(cmList):
    returnList = []
    currentUnit = cmds.currentUnit(q=True, l=True)

    for centimeter in cmList:
        if currentUnit == "mm":
            returnList.append(cmds.convertUnit(centimeter, fromUnit='cm', toUnit='mm'))
        elif currentUnit == "m":
            returnList.append(cmds.convertUnit(centimeter, fromUnit='cm', toUnit='m'))
        elif currentUnit == "im":
            returnList.append(cmds.convertUnit(centimeter, fromUnit='cm', toUnit='inch'))
        elif currentUnit == "ft":
            returnList.append(cmds.convertUnit(centimeter, fromUnit='cm', toUnit='foot'))
        elif currentUnit == "yd":
            returnList.append(cmds.convertUnit(centimeter, fromUnit='cm', toUnit='yard'))
        else:
            returnList.append(centimeter)

    print("clul {}".format(returnList))
    return returnList

# get Manipulators position
def getManipulatorPos(fieldGroup):
    print("step 2")
    cmds.setToolTo('moveSuperContext')
    manipulatorPos = []
    # Move not added yet? Why is it needed - Because you need to put quotation marks to get pos
    manipulatorPos = cmds.manipMoveContext('Move', q=True, p=True)
    print(manipulatorPos)
    manipulatorPos = changeLinearUnitList(manipulatorPos)
    print("manPos {}".format(fieldGroup))
    
    cmds.floatFieldGrp(fieldGroup, e=True, v1=manipulatorPos[0], v2=manipulatorPos[1], v3=manipulatorPos[2])
    # optionVar and G Key repeatLast skipped

def CRMOD_dupMeshAlign():
    # window element sizes
    windowWidth = 350
    windowHeight = 150
    lineHeight = 24
    buttonWM = 66
    checkBoxState = 0

    # if window already exists
    if (cmds.window("Duplicate_Mesh_Align", exists=True)):
        cmds.deleteUI("Duplicate_Mesh_Align")

    # Create window
    cmds.window("Duplicate_Mesh_Align", s=False, t="Duplicate Mesh Align", widthHeight=(windowWidth, windowHeight))

    # Set column Layout
    cmds.columnLayout()
    cmds.text(h=4, l="")  # Adjust Gaps

    # startPos
    cmds.rowLayout(nc=3, cw3=(buttonWM, buttonWM, (buttonWM * 3)), ct3=["right", "right", "right"])
    cmds.text(l="始点座標")
    cmds.button(w=buttonWM, l="取得", c='getManipulatorPos("CRMOD_DMA_strPos_FFldGrp")', ann="移動マニピュレータの座標を取得")
    cmds.floatFieldGrp('CRMOD_DMA_strPos_FFldGrp', h=lineHeight, pre=3, nf=3, cw3=(buttonWM, buttonWM, buttonWM))
    cmds.setParent( '..' )
    cmds.text(h=8, l="")    #Adjust Gaps

    # endPos
    cmds.rowLayout(nc=3, cw3=(buttonWM, buttonWM, (buttonWM * 3)), ct3=["right", "right", "right"])
    cmds.text(l="終点座標")
    cmds.button(w=buttonWM, l="取得", c='getManipulatorPos("CRMOD_DMA_endPos_FFldGrp")', ann="移動マニピュレータの座標を取得")
    cmds.floatFieldGrp('CRMOD_DMA_endPos_FFldGrp', h=lineHeight, pre=3, nf=3, cw3=(buttonWM, buttonWM, buttonWM))
    cmds.setParent( '..' )
    cmds.text(h=8, l="")    # Adjust Gaps

    # Checkbox
    cmds.rowLayout(nc=2)
    cmds.checkBox("placeFirst", w=200, label='Place First', v=True)
    cmds.checkBox("placeLast", w=200, label='Place Last', v=True)
    cmds.setParent( '..' )
    cmds.text(h=8, l="")    # Adjust Gaps
    
    # Number of copies
    cmds.rowLayout(nc=3, cw3=(buttonWM, buttonWM, (buttonWM * 2)), ct3=["right", "right", "right"])
    cmds.text(l="配置数")
    cmds.intField("CRMOD_DMA_DupNum_IFld", w=buttonWM, v=2, min=2, max=99)    #CRMOD_DMA_DupNum_IFld not yet added at the end
    cmds.button(w=buttonWM, l="Done", c="CRMOD_DMA_run()", ann="選択グループor選択メッシュモデルの整列複製")
    cmds.setParent( '..' )

    print("test")

    cmds.showWindow()


CRMOD_dupMeshAlign()
