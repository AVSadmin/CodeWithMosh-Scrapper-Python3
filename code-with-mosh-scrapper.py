import requests
from bs4 import BeautifulSoup as bs
import html5lib
import os

domain = "https://codewithmosh.com"

def download(session, link):
    sc = session.get(link)
    htp = bs(sc.text,'html5lib')

    for section in htp.find_all('div', {'class': 'course-section'}):
        title = section.find('div',{'class':'section-title'}).contents[2].strip()
        
        print("\t#DOWNLOADING SECTION:",title)
        
        if(not os.path.exists(title)):
            os.mkdir(title)
        os.chdir(title)
        
        for lecture in section.find_all('a'):
            if (lecture.find('i',{'class': 'fa-youtube-play'}) is None):
                continue
            lect = session.get(domain+lecture.attrs.get('href'))
            htp = bs(lect.text,'html5lib')
            fileurl = htp.find('div',{'class': 'video-options'}).a.attrs.get('href')
            video_check = session.head(fileurl)
            if(not os.path.exists(video_check.headers.get("X-File-Name"))):
                video = session.get(fileurl)
                with open(video.headers.get("X-File-Name"),'wb') as f:
                    print("\t#->",video.headers.get("X-File-Name"))
                    f.write(video.content)
            else:
                print("\t#->",video.headers.get("X-File-Name"),"(skipped)")
        
        os.chdir("../")
def main():
    print("### DOWNLOADED FILES WILL BE STORED IN THE DIRECTORY OF THE SCRIPT ###")
    if(not os.path.exists("CodeWithMosh")):
        os.mkdir("CodeWithMosh")
    os.chdir("CodeWithMosh")

    session = requests.session()

    # Get session cookie header from user.
    cookie = input("Copy and Paste the \'cookie\' header from your browser after logging in: ")

    session.headers.update({'cookie': cookie})

    cl = session.get(domain+'/courses/enrolled')
    htp = bs(cl.text,'html5lib')

    l1=dict()

    print("Choose the course:")

    for clist in htp.find_all('div',{'class': 'course-list'}):
        for row in clist.find_all('div',{'class': 'row'}):
            course = row.find('a')
            l1[course.find('div',{'class': 'course-listing-title'}).string.strip()] = domain+course.attrs.get('href')
            print(len(l1),". ",course.find('div',{'class': 'course-listing-title'}).string.strip(),sep='')

    # Get course selection from user.
    c = int(input("Enter the Course No. : "))

    # Make directory with course name to download the files.
    print("# SELECTED COURSE:",list(l1.keys())[c-1])

    if(not os.path.exists(list(l1.keys())[c-1])):
        os.mkdir(list(l1.keys())[c-1])
    os.chdir(list(l1.keys())[c-1])

    sc = session.get(list(l1.values())[c-1])
    htp = bs(sc.text,'html5lib')

    # If selected course is a collection, iterate through subcourses.
    if(htp.find('ul',{'class': 'sidebar-nav'}).find('li',{'class': 'selected'}).a.contents[2].string.strip() == "Included Courses"):
        print("#->SUB COURSES AVAILABLE")
        
        l2=dict()
        for clist in htp.find_all('div',{'class': 'enrolled-child-course'}):
            course = clist.find('a')
            l2[course.find('div',{'class': 'course-listing-title'}).string.strip()] = domain+course.attrs.get('href')

        for course,link in l2.items():
            print("#->SELECTED SUB COURSE:",course)
            
            # make directory for subcourse and open it
            if(not os.path.exists(course)):
                os.mkdir(course)
            os.chdir(course)
            
            ssc = session.get(link)
            htp = bs(ssc.text,'html5lib')

            if(htp.find('ul',{'class': 'sidebar-nav'}).find('li',{'class': 'selected'}).a.contents[2].string.strip() != "Included Courses"):
                # calling function to download the course to directory
                download(session,link)

            # return from course directory
            os.chdir("../")
    else:
        download(session,list(l1.values())[c-1])

if __name__ == "__main__":
    main()
