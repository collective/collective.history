*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Create content and check history is working
    Log in as site owner
    Go to homepage
    Add folder    My folder
    Add document    Test document
    Workflow Publish
    Go to history
    Verify history    1   Created      /folder
    Verify history    4   Moved        /my-folder
    Verify history    5   Initialized  /my-folder
    Verify history    6   Created      /document
    Verify history    9   Moved        /test-document
    Verify history    10  Initialized  /test-document
    Click Link    history_next
    Verify history    1   AfterTransition  /test-document
    Verify history    2   ActionSucceeded  /test-document

*** Keywords ***

Go to history
    Go to  ${PLONE_URL}/portal_history

Verify history
    [Arguments]  ${row}  ${what}  ${where}
    Table Row Should Contain    history  ${row}  /${PLONE_SITE_ID}${where}
    Table Row Should Contain    history  ${row}  ${what}
