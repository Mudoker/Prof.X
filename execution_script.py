from appium import webdriver
import json
from datetime import datetime
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy

# Desired capabilities
desired_caps = {
    "platformName": "Android",
    "appium:deviceName": "Android Emulator",
    "appium:appPackage": "com.instructure.candroid",
    "appium:appWaitActivity": "com.instructure.student.activity.LoginLandingPageActivity",
    "appium:app": "C:/Users/huuqu/Downloads/Canvas Student_7.5.0_APKPure.apk",
    "appium:automationName": "UiAutomator2",
}

appium_server_url = "http://127.0.0.1:4723"
capabilities_options = UiAutomator2Options().load_capabilities(desired_caps)

def log_step(
    action,
    sequence_step,
    screenshot,
    text_entry,
    area_edit=0,
    hash_step=None,
    area_view=0,
    area_list=0,
    area_select=0,
    initial_x=0,
    initial_y=0,
    final_x=0,
    final_y=0,
    use_case_tran_type=0,
    network=False,
    acellerometer=False,
    magentometer=False,
    temperature=False,
    gps=False,
    activity=None,
    window=None,
    dyn_gui_components=None,
):
    return {
        "action": action,
        "sequenceStep": sequence_step,
        "screenshot": screenshot,
        "textEntry": text_entry,
        "areaEdit": area_edit,
        "hashStep": hash_step if hash_step is not None else "NO_HASH",
        "areaView": area_view,
        "areaList": area_list,
        "areaSelect": area_select,
        "initialX": initial_x,
        "initialY": initial_y,
        "finalX": final_x,
        "finalY": final_y,
        "useCaseTranType": use_case_tran_type,
        "network": network,
        "acellerometer": acellerometer,
        "magentometer": magentometer,
        "temperature": temperature,
        "gps": gps,
        "screen": {
            "activity": activity if activity else "NO_ACTIVITY",
            "window": window if window else "NO_WINDOW",
            "dynGuiComponents": dyn_gui_components if dyn_gui_components else [],
        },
        "timestamp": datetime.now().isoformat(),
    }

try:
    # Start the timer for elapsed time calculation
    start_time = datetime.now()

    driver = webdriver.Remote(
        command_executor=appium_server_url, options=capabilities_options
    )
    print("Session created successfully")

    test_steps = []

    # Generate a dynamic screenshot filename (consider using a unique identifier)
    screenshot_filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    # driver.save_screenshot(screenshot_filename)  # Capture the screenshot

    # # Get activity and window information
    activity = driver.current_activity
    # window = driver.current_window_handle

    # Get dynamic UI component details
    dyn_gui_components = []
    ui_elements = []
    list_of_elements_id = ["com.instructure.candroid:id/findMySchool"]
    for id in list_of_elements_id:
        ui_elements.append(driver.find_element(by=AppiumBy.ID, value=id))

    print (activity)
    for ui_element in ui_elements:
        component_info = {
            "activity": activity,
            "name": ui_element.get_attribute("content-desc"),
            "idXml": ui_element.get_attribute("resource-id"),
            # "componentIndex": ui_element.get_attribute("index"),
            # "componentTotalIndex": 0,
            "positionX": ui_element.location["x"],
            "positionY": ui_element.location["y"],
            "height": ui_element.size["height"],
            "width": ui_element.size["width"],
            "checkable": ui_element.get_attribute("checkable") == "true",
            "checked": ui_element.get_attribute("checked") == "true",
            "clickable": ui_element.get_attribute("clickable") == "true",
            "enabled": ui_element.get_attribute("enabled") == "true",
            "focusable": ui_element.get_attribute("focusable") == "true",
            "focused": ui_element.get_attribute("focused") == "true",
            "longClickable": ui_element.get_attribute("long-clickable") == "true",
            "scrollable": ui_element.get_attribute("scrollable") == "true",
            "selected": ui_element.get_attribute("selected") == "true",
            "password": ui_element.get_attribute("password") == "true",
            # "itemList": ui_element.get_attribute("item-list") == "true",
            # "calendarWindow": ui_element.get_attribute("calendar-window") == "true",
            "idText": ui_element.text,
            "offset": 0,
            "drawTime": 0.0,
        }
        dyn_gui_components.append(component_info)

    # Log the step
    test_steps.append(
        log_step(
            action="click",
            sequence_step=1,
            screenshot=screenshot_filename,
            text_entry="Clicked on element",
            activity=activity,
            # window=window,
            dyn_gui_components=dyn_gui_components,
        )
    )

    # Calculate elapsed time
    elapsed_time = (datetime.now() - start_time).total_seconds()

    # Get dynamic values for the JSON header
    result = {
        "date": datetime.now().strftime("%b %d, %Y, %I:%M:%S %p"),
        "deviceDimensions": f"{driver.get_window_size()['width']}x{driver.get_window_size()['height']}",
        "executionType": "User-Trace-",
        "executionNum": 12,
        "crash": False,
        "deviceName": driver.capabilities.get("deviceName", "Unknown Device"),
        "elapsedTime": elapsed_time,
        "orientation": driver.orientation,
        "mainActivity": driver.current_activity,
        "androidVersion": driver.capabilities.get("platformVersion", "Unknown Version"),
        "steps": test_steps,
    }

    # Write the JSON to a file
    with open("test_trace.json", "w") as f:
        json.dump(result, f, indent=4)

except Exception as e:
    print("An error occurred:", e)
    if driver:
        driver.quit()
