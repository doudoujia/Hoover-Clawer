# coding: utf-8

# In[4]:


from my_trader import *
from selenium import webdriver
import getpass

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains


def create_driver_session(session_id, executor_url):
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver

    # Save the original function, so we can revert our patch
    org_command_execute = RemoteWebDriver.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': session_id}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    RemoteWebDriver.execute = new_command_execute

    new_driver = webdriver.Remote(command_executor=executor_url, desired_capabilities={})
    new_driver.session_id = session_id

    # Replace the patched function with original function
    RemoteWebDriver.execute = org_command_execute

    return new_driver
#---------------------------
def render_text_contact(get_temp):
    flag = False
    trial =0
    result = pd.DataFrame()
    get_temp = get_temp.text.split("\n")
    # while not flag:
    #     # try:
    #     #     get_temp = get_temp.text.split("\n")
    #     #     flag = True
    #     # except Exception as e:
        #     print "Get text problem"
        #     if trial > 3:
        #         result = [np.NaN,np.NaN,np.NaN,np.NaN]
        #         return result
        #     driver.refresh()
        #     time.sleep(10+2*trial)
        #     trial +=1
            #get_temp = get_temp.get_attribute('innerHTML')
            #print ("!!!! verify: " + get_temp)
            #time.sleep(step_wait)
            #flag= True

    header=["name","position","location","industry"]
    count_header = 0
    #get_temp = get_temp.text.split(":")
    for i in range(len(get_temp)):
        get_temp[i] = get_temp[i].encode('ascii','ignore')
        if ":" in get_temp[i]:
            #flag = True
            get = get_temp[i].split(":")
            result = result.append([get])

        else:
            result = result.append([[header[count_header],get_temp[i]]])
            count_header +=1

    result = result.reindex()
    return result

def get_progress(name):
    mongodb = mongo("hoover")
    progress = pd.DataFrame(list(mongodb.db[name].find())).company_name
    progress = list(progress)
    return progress
#---------------------------
mongodb = mongo("hoover")



# In[11]:


username = raw_input("Username")
password = getpass.getpass()


# In[3]:



#------PARAMETERS---------------

step_wait = 2
page_wait = 5
collection_name = "California Minority Wholesaler"
list_row_number = 6  #input the list position of the list you want to crawl, starting 0
try:
    progress = get_progress(collection_name)
except:
    progress = []

#flag initialize
from_beginning =  True

rebot_flag = False #default to be True to start with the program

just_open_window = True  #default to be False to start with the program
#-------------------------------


# In[37]:



if rebot_flag:
    #reset flag
    rebot_flag = False
#===============OPEN BROWER=============================================
    driver=webdriver.Firefox()
    session_id =driver.session_id
    executor_url =driver.command_executor._url
    driver.implicitly_wait(5)

    driver.get('https://signon.onesource.com/Web/Logon/Signin.aspx')
    time.sleep(step_wait)
    driver.implicitly_wait(5)
    driver.find_element_by_id("username").clear()
    driver.find_element_by_id("username").send_keys(username)
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys(password)
    driver.find_element_by_id("btnSignIn").click()
    time.sleep(step_wait)
    driver.implicitly_wait(10)
    driver.find_element_by_link_text("Lists").click()
    time.sleep(step_wait)
    driver.implicitly_wait(10)

    # list selector

#    list_ele = driver.find_elements_by_class_name("name-row")
#    get = list_ele[list_row_number]
#    get.find_element_by_tag_name("a").click()

    list_ele = driver.find_elements_by_link_text(collection_name)[1]
    driver.execute_script("arguments[0].click();", list_ele)
    #page info

    current_page = driver.find_element_by_class_name("current-page")
    current_page=current_page.get_attribute('innerHTML')
    current_page = int(current_page)

    total_page = driver.find_element_by_class_name("total-page")
    total_page=total_page.get_attribute('innerHTML')
    total_page = int(total_page)
    if not from_beginning:
        last_page = driver.find_element_by_class_name("last-page")
        driver.execute_script("arguments[0].click();", last_page)
        time.sleep(step_wait)
#================================================================================
if just_open_window:
    raise SystemExit(0)
while True:
    try:
        driver.implicitly_wait(100)
        current_page = driver.find_element_by_class_name("current-page")
        current_page=current_page.get_attribute('innerHTML')
        current_page = int(current_page)

        # company selector
        company_list = driver.find_elements_by_class_name("clickable")
        name_list=[]
        for i in range(len(company_list)):
            name_list.append(company_list[i].text)

        for i in name_list:
            #clear_output()

            #company_list = driver.find_elements_by_class_name("clickable")
            #get_company = company_list[i]
            if i in progress:
                print (i+ " already in database, skipping")
                continue
            page_trial = 0
            while True:
                try:
                    if page_trial <3:
                        time.sleep(page_wait)
                        driver.implicitly_wait(10)
                        get_company = driver.find_element_by_link_text(i)
                        driver.execute_script("return arguments[0].scrollIntoView();", get_company)
                        driver.execute_script("arguments[0].click();", get_company)

                        #company_list[i].click()
                        WebDriverWait(driver, 80).until(EC.presence_of_element_located((By.ID, "totalContacts")))
                        time.sleep(step_wait)

                        #get basic information
                        info = {}
                        address = driver.find_element_by_class_name("company-address").text
                        company_name = driver.find_element_by_class_name("name").text
                        business_description = driver.find_element_by_class_name("description").text.split("\n")[1]
                        industry = driver.find_element_by_class_name("industry").text.split("\n")[2].split(":")[1][12:]
                        sic = driver.find_element_by_class_name("industry").text.split("\n")[2].split(":")[1][0:8]
                        try:
                            website = driver.find_element_by_class_name("url").text
                            info["website"] = website
                        except:
                            print ("no website found")
                            info["website"]=np.NaN

                        data = driver.find_elements_by_class_name("data-container")
                        for i in range(len(data)):

                            try:
                                label=data[i].find_element_by_class_name("data-label")
                            except:
                                continue
                                #label=data[i].find_element_by_class_name("data-label wide")
                            value=data[i].find_elements_by_class_name("data-value")
                            value = value[0].text
                            label = label.text
                            label = label.encode('ascii','ignore')
                            info[label] = value

                        info["address"] = address
                        info["company_name"] = company_name
                        info["business_description"] = business_description
                        info["industry"] = industry
                        info["sic"] = sic

                        mongodb.db[collection_name].insert_one(info)

                        #get highlights
                        highlights = pd.DataFrame()
                        get_temp = driver.find_element_by_class_name("highlights").text
                        get_temp = get_temp.split("\n")
                        for i in range(len(get_temp)):
                            get_temp[i] = get_temp[i].encode('ascii', 'ignore')
                            get = get_temp[i].split(":")
                            highlights = highlights.append([get])
                        highlights = highlights[2:]
                        highlights = highlights.set_index(0)
                        highlights=json.loads(highlights.to_json()).values()[0]
                        mongodb.db[collection_name].update_one({"company_name":company_name},{"$set":highlights},upsert=True)
                        print (company_name + ": business information got")
                        break
                    else:
                        break
                except Exception as e:
                    print ("----page_info----")
                    print e
                    print ("---------------")
                    driver.back()
                    driver.forward()
                    page_trial +=1

            #Get contacts
            contacts_flag = False
            contact_trial = 0
            while not contacts_flag:
                try:
                    contacts = driver.find_element_by_id("totalContacts").text
                    contacts = int(contacts)
                    contacts_flag = True
                except:
                    #print ("contact number didn't come out yet")
                    continue
            while True:
                try:
                    if contacts != 0 and contact_trial<3:
                        try:
                            driver.find_element_by_id("company_contacts").click()
                        except:
                            driver.execute_script("arguments[0].click();", driver.find_element_by_id("company_contacts"))
                        time.sleep(step_wait)
                        driver.implicitly_wait(20)
                        time.sleep(step_wait)
                        WebDriverWait(driver, step_wait).until(EC.presence_of_element_located((By.CLASS_NAME, "detail-container")))
                        contacts = driver.find_elements_by_class_name("detail-container")

                        contacts = driver.find_elements_by_class_name("search-result-container")
                        result = []
                        for i in range(len(contacts)):

                            temp = render_text_contact(contacts[i])
                            temp = temp.set_index(temp[0])
                            temp = temp.drop(0,axis=1)
                            result.append(json.loads(temp.to_json()).values())
                        mongodb.db[collection_name].update_one({"company_name":company_name},{"$set":{"contact":result}},upsert=True)
                        print (company_name + ": contacts information got")
                        driver.back()
                        break
                    else:
                        print ("no contact available")
                        mongodb.db[collection_name].update_one({"company_name":company_name},{"$set":{"contact":"None"}},upsert=True)
                        break

                # page wait time

                except Exception as e:
                    print ("--contact------")
                    print e
                    print ("---------------")
                    driver.back()
                    driver.forward()
                    contact_trial +=1

            #finished one company
            progress.append(company_name)
            driver.back()
    except Exception as e:
        print ("--back to list------")
        print e
        print ("---------------")
        driver.refresh()
        continue
        # next page
    if from_beginning:
        if current_page <=total_page:
            try:
                next_page = driver.find_element_by_class_name("next-page")
                driver.execute_script("arguments[0].click();", next_page)
                time.sleep(page_wait)
                driver.implicitly_wait(10)
                page_changed = True
            except Exception as e:
                print ("------Page change error-----")
                driver.refresh()
                time.sleep(5)
                continue

        else:
            break
    else:
        if current_page>27:
            #print "previous page"
            try:
                last_page = driver.find_element_by_class_name("previous-page")
                driver.execute_script("arguments[0].click();", last_page)
                time.sleep(page_wait)
                driver.implicitly_wait(10)
            except Exception as e:
                print ("------Page change error-----")
                driver.refresh()
                time.sleep(5)
                continue
        else:
            break
driver.quit()
#================================================    
#Getting hoover data


hoover_data = pd.DataFrame(list(mongodb.db[collection_name].find())).drop("",axis = 1)
hoover_data=hoover_data.set_index("company_name")
hoover_contact_temp=hoover_data.loc[:,"contact"].dropna()
#Getting hoover contact data
hoover_contacts = pd.DataFrame()
for i in range(len(hoover_contact_temp)):
    if hoover_contact_temp.iloc[i] != "None":
        for j in hoover_contact_temp.iloc[i]:
            try:
                temp = pd.DataFrame(j,index=[hoover_contact_temp.index[i]])
                hoover_contacts = hoover_contacts.append(temp)
            except Exception as e:
                print (e)
                #input("any enter to continue")
                continue

hoover_contacts.index.name = "company_name"
hoover_data.to_csv(collection_name + ".csv",encoding="utf-8")
hoover_contacts.to_csv(collection_name+"_contacts.csv")




