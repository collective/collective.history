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
    Rename Content Title    test-document  New document title
    Remove Content    test-document
    Go to history
    Verify history    1   created       /my-folder
    Verify history    2   created       /test-document
    Verify history    3   statechanged  /test-document
    Import library  Dialogs
    Pause execution
    Verify history    4   moved         /test-document
    Verify history    5   deleted       /test-document

*** Keywords ***

Go to history
    Go to  ${PLONE_URL}/portal_history

Verify history
    [Arguments]  ${row}  ${what}  ${where}
    Table Row Should Contain    history  ${row}  /${PLONE_SITE_ID}${where}
    Table Row Should Contain    history  ${row}  ${what}
