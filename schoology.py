import json
import requests
import sys
from bs4 import BeautifulSoup as bS
from datetime import datetime


def json_format(success, message_or_grades):
  """
  Args:
      success: boolean if scraping was successful
      message_or_grades: a message for errors or grade data in JSON format

  Returns:
      A JSON formatted response
  """

  if success:
    return json.dumps({'success': True, 'new_grades': message_or_grades})

  return json.dumps({'success': False, 'message': message_or_grades})


def status(progress, message):
  return json.dumps({'progress': progress, 'message': message})
  
class Scraper:
    def __init__(self):
        """Inits with a session"""
        self.session = requests.Session()
        self._progress = 0
        self._message = ""
        print(status(self._progress, self._message))

    @property
    def progress(self):
        return self._progress

    @property
    def message(self):
        return self._message

    @progress.setter
    def progress(self, value):
        self._progress = value
        print(status(self._progress, self._message))

    @message.setter
    def message(self, value):
        self._message = value
        print(status(self._progress, self._message))


class BasisScraper(Scraper):
  def login(self, email, _password):
    url = "https://app.schoology.com/login?destination=courses"

    payload = {'mail': email,
               'pass': _password,
               'form_id': 's_user_login_form'}

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'origin': 'https://app.schoology.com',
      'referer': 'https://app.schoology.com/login?destination=courses/courses',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
    }

    resp = self.session.post(url, headers=headers, data=payload, allow_redirects=False)
    self.progress = 5
    self.message = "Logged in!"
    if len(resp.cookies) == 0:
      self.progress = 0
      print(json_format(False, "Incorrect login details."))
      sys.exit()

    return True

  def get_present(self):
    url = "https://app.schoology.com/courses/courses"

    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-US,en;q=0.9',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive',
      'referer': 'https://app.schoology.com/login?destination=courses/courses',
      'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
    }

    resp = self.session.post(url, headers=headers)
    self.progress = 20
    self.message = 'Searching for courses...'

    soup = bS(resp.text, 'html.parser')

    classes = soup.find_all('li', class_="course-item")

    total_course_count = len(classes)
    scraped_course_count = 0
    initial_progress = self.progress
    max_progress = 100
    self.message = 'Synced ' + str(scraped_course_count) + ' of ' + str(total_course_count) + ' courses...'
    self.progress = initial_progress + (max_progress - initial_progress) * scraped_course_count / total_course_count
    data = []
    for class_ in classes:
      datasub = []
      self.message = 'Synced ' + str(scraped_course_count) + ' of ' + str(total_course_count) + ' courses...'
      self.progress = initial_progress + (max_progress - initial_progress) * scraped_course_count / total_course_count
      class_name = str(class_.find('span', class_='course-title').get_text())
    
      if "office" in class_name.lower() or "lunch" in class_name.lower():
        total_course_count -= 1
        continue
      
      section = str(class_.find('div', class_='section-item').get_text())

      link = str(class_.find('a').get('href'))
      
      scraped_course_count += 1
      datasub.append(class_name)
      datasub.append(section)
      datasub.append(link)
      import time
      time.sleep(0.35) #prevent requests
      url = f"https://app.schoology.com{link}/materials?list_filter=assignments&ajax=1&style=full"

      headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'referer': 'https://app.schoology.com/login?destination=courses/courses',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
      }

      resp = self.session.post(url, headers=headers)
      newsoup = str(bS(resp.text, 'html.parser'))
      newsoup = newsoup.replace("\\u003C","<").replace('\\u0022','"').replace('\\u003E','>').replace("\\u0027","'").replace("\\u00a0"," ").replace("\\u0026","&").replace("\\u201c","“").replace("\\u2019s","’").replace("\\u201d","”").replace("\\u00e9","é").replace("\\u2026","…").replace("\\u2013","-").replace("\\n","").replace("\\", "");
      
      with open('temp.html','w') as out:
        print(newsoup,file=out)
      with open("temp.html") as fp:
        newsoup = bS(fp, 'html.parser')
      assignments_= newsoup.find_all('div', "s-common-block has-control control-small has-media media-small")
      assignments = []
      for assignment in assignments_:
        datasubsub = []
        try:
          folder = str(assignment.find('span', class_='infotip-content').get_text())
        except:
          folder = ''
        datasubsub.append(folder)
        name = str(assignment.find('div', class_='s-common-block_title').get_text())
       
        datasubsub.append(name)
        description = assignment.find('div',class_='s-common-block_copy')
        if description==None:
          description = ''
        else:
          description = str(description.get_text())
        datasubsub.append(description)
        newlink = str(assignment.find('div', class_='s-common-block_title')).replace('<div class="s-common-block_title">','').replace('</div','').strip("<a href=\"")
        time.sleep(0.35)
        a = newlink.index('"')
        newlink = newlink[0:a]
        datasubsub.append(newlink)
        url = "https://app.schoology.com"+newlink
        
        headers = {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
          'Accept-Encoding': 'gzip, deflate, br',
          'Accept-Language': 'en-US,en;q=0.9',
          'Cache-Control': 'max-age=0',
          'Connection': 'keep-alive',
          'referer': 'https://app.schoology.com/login?destination=courses/courses',
          'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
        }

        resp = self.session.post(url, headers=headers)   
        newnewsoup = bS(resp.text, 'html.parser')
        due = str(newnewsoup.find('p',class_='due-date'))
        grade = str(newnewsoup.find('div',class_='grading-grade'))
        datasubsub.append(str(due))
        datasubsub.append(str(grade))
        assignments.append(datasubsub)
      datasub.append(assignments)
      url = f"https://app.schoology.com{link}/members"

      headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'referer': 'https://app.schoology.com/login?destination=courses/courses',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31',
      }

      resp = self.session.post(url, headers=headers)
      newnewsoup = bS(resp.text, 'html.parser')
      # try:
      #   membercount = int(str(newnewsoup.find('span',class_="total").get_text)
      # except Exception as e::
      #   print("Error")
      #   membercount = 0
      members = []
      members_ = newnewsoup.find_all('class',class_="enrollment-admin")
      for member in members_:
        members.append([True, member.find('class','user-name').replace('<td class="user-name">','').replace('<b>','').replace('</b>','').replace('</span></div></td>',''),member.find('class','user-picture')])
      members_ = newnewsoup.find_all('class',class_="enrollment-member")
      for member in members_:
        members.append([False, member.find('class','user-name'),member.find('class','user-picture')])
      #datasub.append(membercount)
      datasub.append(members)
      data.append(datasub)
    
      
        
    
    with open("main.json","w") as out:
     json.dump(data,out,indent=4)

    
      


if __name__ == "__main__":
  school = "basis"
  if school == "basis":
    user = sys.argv[1].lower()
    password = sys.argv[2].lower().strip()
    bs = BasisScraper()
    try:
      if bs.login(user, password):
        bs.get_present()
    except requests.Timeout:
      print(json_format(False, "Could not connect to Schoology."))
    # except Exception as e:
    #   # Error when something in PowerSchool breaks scraper
    #   print(json_format(False, f"An Unknown Error occurred. Contact support.  Error {e}"))
  