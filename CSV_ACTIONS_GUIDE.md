# 📋 CSV Actions Guide - Complete Reference

## 🎯 **Basic Actions**

### **Navigation**
```csv
action,xpath,data
open_url,https://example.com,
```

### **Text Input**
```csv
action,xpath,data
type,//input[@id="username"],admin
type,//input[@name="password"],password123
```

### **Clicking**
```csv
action,xpath,data
click,//button[@id="loginButton"],
click,//a[text()="Sign In"],
```

### **Verification**
```csv
action,xpath,data
verify,text=Welcome,
verify,//div[@id="success-message"],
```

## ⏱️ **Wait Actions**

### **Fixed Time Wait**
```csv
action,xpath,data
wait,5,
wait,10,
```

### **Wait for Element to Appear**
```csv
action,xpath,data
wait_for_element,//div[@id="loading-complete"],
wait_for_element,//span[text()="Success"],
```

### **Wait for Element to be Clickable**
```csv
action,xpath,data
wait_for_clickable,//button[@id="submit"],
wait_for_clickable,//a[text()="Continue"],
```

### **Wait for Element to be Visible**
```csv
action,xpath,data
wait_for_visible,//div[@class="popup"],
wait_for_visible,//img[@id="profile-pic"],
```

## 📋 **Dropdown Selection**

### **Select by Visible Text**
```csv
action,xpath,data
select_dropdown,//select[@id="country"],United States
select_dropdown,//select[@name="state"],California
select,//select[@id="category"],Electronics
```

### **Select by Value (Alternative)**
```csv
action,xpath,data
select_dropdown,//select[@id="country"],US
select_dropdown,//select[@name="state"],CA
```

## 📁 **File Upload**

### **Upload Image**
```csv
action,xpath,data
upload_file,//input[@type="file"],C:\Users\Admin\Pictures\profile.jpg
upload,//input[@id="file-upload"],D:\Documents\resume.pdf
```

### **Upload Multiple Files**
```csv
action,xpath,data
upload_file,//input[@type="file"],C:\file1.jpg C:\file2.jpg
```

## 🖱️ **Advanced Mouse Actions**

### **Double Click**
```csv
action,xpath,data
double_click,//div[@id="editable-text"],
double_click,//span[@class="selectable"],
```

### **Right Click**
```csv
action,xpath,data
right_click,//div[@id="context-menu-trigger"],
right_click,//img[@id="profile-pic"],
```

### **Hover**
```csv
action,xpath,data
hover,//span[@class="tooltip-trigger"],
hover,//button[@id="dropdown-trigger"],
```

## 📜 **Scrolling**

### **Scroll to Element**
```csv
action,xpath,data
scroll_to,//footer[@id="page-footer"],
scroll_to,//div[@id="bottom-content"],
```

## 🖼️ **Frame Handling**

### **Switch to Frame**
```csv
action,xpath,data
switch_to_frame,//iframe[@id="embedded-form"],
switch_to_frame,//iframe[@name="content"],
switch_to_frame,,frame-name
```

### **Switch Back to Default**
```csv
action,xpath,data
switch_to_default,
```

## 🧹 **Field Management**

### **Clear Field**
```csv
action,xpath,data
clear,//input[@id="username"],
clear,//textarea[@id="description"],
```

## 🔧 **JavaScript Actions**

### **JavaScript Click (for custom components)**
```csv
action,xpath,data
js_click,//button[@id="custom-dropdown"],
js_click,//span[text()="Open bento menu"],
js_click,//div[@class="custom-select"],
```

### **Execute Custom JavaScript**
```csv
action,xpath,data
execute_js,return document.querySelector('#myElement').click();,
execute_js,return window.scrollTo(0, document.body.scrollHeight);,
execute_js,return document.getElementById('hidden-field').value = 'test';,
```

## 📝 **Complete Example**

```csv
action,xpath,data
open_url,https://example.com/registration,
wait,2,
type,//input[@id="firstName"],John
type,//input[@id="lastName"],Doe
type,//input[@id="email"],john.doe@example.com
select_dropdown,//select[@id="country"],United States
select_dropdown,//select[@id="state"],California
upload_file,//input[@type="file"],C:\Users\Admin\Pictures\profile.jpg
wait_for_element,//div[@id="upload-success"],
verify,text=File uploaded successfully,
click,//button[@id="submit"],
wait_for_visible,//div[@class="success-message"],
verify,text=Registration completed,
```

## 🎯 **Common XPath Patterns**

### **By ID**
```csv
//input[@id="username"]
//button[@id="submit"]
//div[@id="content"]
```

### **By Class**
```csv
//div[@class="form-group"]
//button[@class="btn-primary"]
//span[@class="error-message"]
```

### **By Text**
```csv
//button[text()="Submit"]
//a[text()="Sign In"]
//span[text()="Welcome"]
```

### **By Attribute**
```csv
//input[@name="email"]
//button[@type="submit"]
//a[@href="/login"]
```

### **By Partial Text**
```csv
//span[contains(text(),"Welcome")]
//div[contains(@class,"success")]
//a[contains(@href,"dashboard")]
```

## ⚠️ **Important Notes**

1. **File Paths**: Use absolute paths for file uploads
2. **Wait Times**: Use reasonable wait times (1-10 seconds)
3. **XPath**: Use specific, stable XPath selectors
4. **Data**: Leave empty for actions that don't need data
5. **Testing**: Test your CSV files with small datasets first

## 🚀 **Running Your Enhanced Tests**

```bash
python csv_action_handler.py enhanced_sample_actions.csv
```

This will execute all the actions and generate an Allure report with screenshots!
