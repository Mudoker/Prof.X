from email.mime import image
from posixpath import split
import cv2
import numpy as np
import argparse
import colour  # for delta_E calc :  pip3 install colour-science

import json, os, sys
import difflib

scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)
import imageUtilities as imgUtil
import xmlUtilities
import labelPredictor


detailedResult = True
tracePlayerGenerated = True


def load_arguments():
    """construct the argument parse and parse the arguments"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--appName", required=True, help="appName")
    ap.add_argument("-b", "--bugId", required=True, help="bug id")

    args = vars(ap.parse_args())
    return args


def read_json(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def create_trigger_list():
    listOfTriggerWords = []
    listOfTriggerWords.append("theme")
    listOfTriggerWords.append("night")

    # Trigger words for Canvas
    listOfTriggerWords.append("dark")
    listOfTriggerWords.append("light")

    return listOfTriggerWords


def create_component_list():
    """List of components potentially used for theme change"""
    listOfComponents = []
    listOfComponents.append("switch")
    listOfComponents.append("radio")
    listOfComponents.append("checkbox")
    listOfComponents.append("toggle")

    return listOfComponents


def check_if_theme_set(
    image_name, xmlPath, tapPos, tappedComponent, listOfTriggerWords
):
    """checks if the interacted component was theme or if it was switch, toggle beside the word theme"""
    """returns two boolean for theme Changed? , one step theme changed?"""
    try:
        tapY = tapPos[-1] if tapPos else "-1"
        tapX = tapPos[-2] if len(tapPos) > 1 else "-1"
        # print(image_name)
        # in case no tap info
        if tapX == "-1" or tapY == "-1":
            return False, False
        text = imgUtil.readTextInImage(image_name)
        listOfComponents = create_component_list()

        # Need to be more dynamic
        if "theme" in text.lower():
            # print(xmlPath, "THEME SET", image_name)
            return True, False
        else:
            startY, endY = xmlUtilities.findParentBoundOfMatchingNode(
                xmlPath, listOfTriggerWords
            )

            # check if clicked component is at same height as the word "theme"
            if int(startY) < int(tapY) < int(endY):
                if any(words in tappedComponent.lower() for words in listOfComponents):
                    return True, True

            # Check if clicked component is within the horizontal bounds
            if int(startX) <= int(tapX) <= int(endX):
                if any(words in tappedComponent.lower() for words in listOfComponents):
                    return True, True

            return False, False

        return False, False

    except Exception as e:
        return False, False


def find_xml_from_screenshot(imagename, stepNum, args):
    """
    Matches the xml file name with the screenshot name
    input: screenshot name, step number, args
    output: xml file name
    """

    xmlName = ""
    if tracePlayerGenerated:
        # xmlName = imagename.split(".User-Trace")[0]
        # xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"

        # Work for Canvas specifically
        # Input: setting-light.canvas.png
        # Output: setting-light.canvas.xml
        xmlName = imagename + ".xml"
    else:
        xmlName = imagename.split("screen")[0]
        xmlName += "ui-dump.xml"

    return os.path.join(args["bugId"], os.path.join("xmls", xmlName))


def get_step_details(step):

    screen_index = step["sequenceStep"]
    tapPosition = step["textEntry"].split(" ")
    if "dynGuiComponent" in step:
        clicked_comp_name = step["dynGuiComponent"]["name"]
    else:
        clicked_comp_name = ""

    return screen_index, tapPosition, clicked_comp_name


def find_trigger_reading_image(
    list_of_steps, screen_count_map, list_of_trigger_words, args
):
    """Input: steps list from execution.json
    Output: list of screen numbers where the trigger was clicked"""

    # State variables
    is_theme_changed = False
    is_post_theme_change_step = False
    updated_screen_after_theme_change = None
    is_updated_screen_found = False
    updated_screen_index = None
    updated_screen_xml = None

    # Variables to store the trigger screen and affected screens
    trigger_screen_list = []
    trigger_screen_text = ""
    screens_updated_after_theme_change = {}
    screen_to_xml_map = {}
    bug_id = args["bugId"]
    theme_change_success_map = {}
    pre_theme_image_status = ""
    previous_screen_image = ""

    # Iterate through each step
    for step in list_of_steps:
        start_screen_image = step["screenshot"]
        clicked_component_image = start_screen_image.replace("augmented", "gui")
        result_screen_image = start_screen_image.replace("_augmented", "")

        # Get the step details
        current_screen_index, tap_position, clicked_component_name = get_step_details(
            step
        )
        clicked_component_image_path = os.path.join(bug_id, clicked_component_image)
        xml_path = find_xml_from_screenshot(
            start_screen_image, current_screen_index, args
        )

        screen_to_xml_map[result_screen_image] = xml_path

        if (
            is_theme_changed
            and is_updated_screen_found
            and current_screen_index > updated_screen_index
        ):
            screens_updated_after_theme_change[
                updated_screen_after_theme_change
            ].append(result_screen_image)

        if not is_theme_changed:
            # Check if theme was set
            theme_change_detected, is_post_theme_change_step = check_if_theme_set(
                clicked_component_image_path,
                xml_path,
                tap_position,
                clicked_component_name,
                list_of_trigger_words,
            )

            # Process theme change
            if theme_change_detected:
                if not is_post_theme_change_step:
                    xml_path = find_xml_from_screenshot(
                        previous_screen_image, current_screen_index - 1, args
                    )

                is_theme_changed = True
                is_updated_screen_found = False
                pre_theme_image_status = imgUtil.is_image_light(
                    os.path.join(bug_id, start_screen_image)
                )
        else:
            if is_post_theme_change_step:
                text_in_current_screen = sorted(xmlUtilities.readTextInXml(xml_path))
                sequence_matcher = difflib.SequenceMatcher(
                    None, text_in_current_screen, trigger_screen_text
                )
                match_ratio = sequence_matcher.ratio()

                if match_ratio >= 0.90:
                    is_updated_screen_found = True
                    updated_screen_after_theme_change = result_screen_image
                    updated_screen_xml = xml_path
                    updated_screen_index = current_screen_index
                    trigger_screen_list.append(updated_screen_after_theme_change)
                    screens_updated_after_theme_change[
                        updated_screen_after_theme_change
                    ] = []
                    post_theme_image_status = imgUtil.is_image_light(
                        os.path.join(bug_id, result_screen_image)
                    )
                    theme_change_success_map[updated_screen_after_theme_change] = (
                        pre_theme_image_status != post_theme_image_status
                    )

        previous_screen_image = start_screen_image

    return (
        trigger_screen_list,
        screens_updated_after_theme_change,
        screen_to_xml_map,
        theme_change_success_map,
    )


def check_if_keyboard_visible(imageName):
    img = cv2.imread(imageName)
    croppedA = imgUtil.crop_keyboard(img)
    return labelPredictor.has_keyboard(croppedA)


def main():

    args = load_arguments()
    bugId = args["bugId"]
    screen_count_map = {}

    data = read_json(os.path.join(bugId, "Execution-12.json"))
    listOfTriggerWords = create_trigger_list()

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  ORACLE FOR THEME CHANGE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            )
            (
                triggerList,
                correct_affected_image_map,
                image_xml_map,
                themeChangeSuccess,
            ) = find_trigger_reading_image(
                listOfSteps, screen_count_map, listOfTriggerWords, args
            )

    if len(triggerList) >= 1:
        print("Theme change detected")
    else:
        print("Theme change not detected")
        return

    print(
        "--------------------------- Was theme changed successfully? -------------------------------"
    )
    # check if theme changed successfully
    for trigger in triggerList:
        if themeChangeSuccess[trigger]:
            print("Theme changed successfully")
        else:
            print("Theme change was not successful")
            return

    print(
        "---------------------------- Did theme match in all screen? -------------------------------"
    )
    # check if theme of all screen match
    for trigger in triggerList:
        all_affected_images = correct_affected_image_map[trigger]
        hasKeyboard = check_if_keyboard_visible(os.path.join(bugId, trigger))
        print(trigger, bugId)
        lab1 = imgUtil.get_lab_val(os.path.join(bugId, trigger), hasKeyboard, None)
        for affected_image in all_affected_images:
            hasKeyboard = check_if_keyboard_visible(os.path.join(bugId, affected_image))
            xmlPath = image_xml_map[affected_image]
            bounds = getFocusedElement(xmlPath)

            lab2 = imgUtil.get_lab_val(
                os.path.join(bugId, affected_image), hasKeyboard, bounds
            )
            is_theme_matching(lab1, lab2, trigger, affected_image)

    print(
        "---------------------------- Did all text show in dark theme? ------------------------------"
    )
    # check if text is seen in all screen after theme change. Compare ocr result with text in xml
    for trigger in triggerList:
        all_affected_images = correct_affected_image_map[trigger]
        for affected_image in all_affected_images:
            xmlPath = image_xml_map[affected_image]
            is_text_displayed(bugId, affected_image, xmlPath)


def preprocess_text(txt):
    result = []
    for t in txt:
        t = t.replace("\n", " ").lower().strip()
        t = t.replace("  ", " ")
        result.append(t)

    return result


def getFocusedElement(xmlPath):
    bounds = xmlUtilities.readBoundOfFocusedElement(xmlPath)
    return bounds
    # print(bounds)


def is_text_displayed(bugId, affected_image, xmlPath):
    txt_from_img = sorted(imgUtil.read_text_on_screen(bugId, affected_image))
    txt_from_xml = sorted(xmlUtilities.readTextInXml(xmlPath))
    seq_mat = difflib.SequenceMatcher()
    # print(preprocess_text(txt_from_img))
    txt_from_img = preprocess_text(txt_from_img)
    txt_from_xml = preprocess_text(txt_from_xml)

    diff = set(txt_from_xml) - set(txt_from_img)
    bad_frac = len(diff) / len(txt_from_xml)
    # print(diff)
    # print(affected_image)
    # seq_mat.set_seqs(txt_from_img, txt_from_xml)
    # print(txt_from_img)
    # print(txt_from_xml)
    # print(txt_from_xml)
    # print(txt_from_img)
    # match_ratio = seq_mat.ratio()
    # if match_ratio >= 0.50:
    if bad_frac <= 0.5:
        print("Most text shows in ", affected_image)
    else:
        print("{:.2%} of text didn't show in".format(bad_frac), affected_image)
        # print("Text didn't show in ", affected_image, bad_ratio, "%")


def is_theme_matching(lab1, lab2, trigger, affected_image):
    delta_E = colour.delta_E(lab1, lab2)

    # A result less than 2 is generally considered to be perceptually equivalent.
    if delta_E > 2:
        print(
            "Test failed : the theme change is inconsistent on image",
            affected_image,
        )
    else:
        print("Test passed : the theme is consistent on image", affected_image)
    global detailedResult
    if detailedResult:
        print(
            "===================================== DETAILED RESULT ====================================="
        )

        print(
            "If delta_E value of two images is less than 2, the images are generally considered to be perceptually equivalent."
        )
        print(
            "The delta_E value for this images compared to ",
            trigger,
            " is ",
            delta_E,
        )
        showContext = False
        print(
            "-------------------------------------------------------------------------------------------"
        )


if __name__ == "__main__":
    main()
