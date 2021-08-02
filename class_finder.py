import requests
from bs4 import BeautifulSoup
#this fuction return the link of professor's profile from rate my prof
def link_extractor(firstname, lastname):
    baselink = "https://www.ratemyprofessors.com/search.jsp?query="
    finalLink = baselink + firstname + '+' + lastname
    r = requests.get(finalLink)
    soup = BeautifulSoup(r.text, 'html.parser')
    results = soup.find_all('li', attrs={'class':'listing PROFESSOR'})
    listOne = []
    for i in results:
        listOne.append(str(i))
    x = []
    for i in range(len(listOne)):
        if "Georgia Institute of Technology" in listOne[i]:
            x.append(listOne[i])
    results = []
    for item in x:
        item = item.split('>')
        newsite = item[1]
        newsite = newsite[10:-1]
        finalsite = 'https://www.ratemyprofessors.com' + newsite
        results.append(finalsite)
    return results
    
#this fuction returns avgrating, difficulty, percent of people who will take the course again
def data_extractor(results):
    rating = 0
    difficulty = 0
    takeagain = 0
    for i in range(len(results)):
        item = results[i]
        newdata = requests.get(item)
        newsoup = BeautifulSoup(newdata.text, 'html.parser')
        newresults = newsoup.find_all('script')
        newresults = str(newresults[-3])
        ratingIndex = newresults.find("avgRating")
        current_rating = newresults[ratingIndex+11:ratingIndex+14]
        if current_rating[-1] == '\"':
            current_rating = float(current_rating[:-2])
        else:
            current_rating = float(current_rating)
        if current_rating > rating:
            rating = current_rating
        difficultyIndex = newresults.find("avgDifficulty")
        current_difficulty = newresults[difficultyIndex + 15 :difficultyIndex + 18]
        if current_difficulty[-1] == '\"':
            current_difficulty = float(current_difficulty[:-2])
        else:
            current_difficulty = float(current_difficulty)
        if current_difficulty > difficulty:
            difficulty = current_difficulty
        againindex = newresults.find("wouldTakeAgainPercent")
        a = newresults[againindex + 23:againindex + 26]
        if a[-1] == '\"':
            a = float(a[:-2])
        elif a[-1] == ',':
            a = float(a[:-2])
        else:
            a = float(a)

        if a > takeagain:
            takeagain = a
            if int(takeagain) < takeagain: 
                takeagain = int(takeagain) + 1
    return[rating, difficulty, takeagain]

#this funtion returns avg gpa and percent of A's
def get_grades(course_code_in_upper_case, firstname, lastname):
    baselink = 'https://critique.gatech.edu/course.php?id='
    link = 'https://critique.gatech.edu/prof.php?id='
    finallink = baselink + course_code_in_upper_case
    fullname = (lastname+firstname).upper()
    if '-' in fullname:
        x = fullname.split('-')
        fullname = x[0] + x[-1]
    link += fullname
    r = requests.get(finallink)
    soup = BeautifulSoup(r.text, 'html.parser')
    r2 = requests.get(link)
    soup2 = BeautifulSoup(r2.text, 'html.parser')
    results = soup.find_all('tr', attrs={'class':fullname})
    results2 = soup2.find_all('table', attrs={'class':"table table-striped table-ordered"})
    listOne = []
    for i in results:
        listOne.append(str(i))
    a = [str(results2[0])]
    if len(listOne) > 0:
        listOne = listOne[0].split('<td>')
        avggpa = float(listOne[3][:-5])
        percentage = int(listOne[4][:-5])
        return [avggpa, percentage]
    elif len(a) == 1:
        a = a[0].split('<tr>')
        a = a[-1].split('</td><td>')
        if a[0][-4:] != 'ble>':
            avggpa = float(a[0][-4:])
            percentage = int(a[1])
            return [avggpa, percentage]
        else:
            return [0,0]
    else:
        return ['0','0']

#this functions returns data from oscar, month in argument should be the start of semester ie '08', year should be the year of semester ie '2020', symbol should be
# like 'CS', 'MATH', code should be like '1332', '1554', all of these should be entered as strings.
def oscar_data(month, year, symbol_in_uppercase, code):
    x = []
    baselink_one = 'https://oscar.gatech.edu/pls/bprod/bwckctlg.p_disp_listcrse?term_in='
    baselink_two = str(year) + str(month)
    baselink_three = '&subj_in='
    baselink_four = str(symbol_in_uppercase)
    baselink_five = '&crse_in='
    baselink_six = str(code)
    baselink_seven = '&schd_in=%'
    firstlink = baselink_one + baselink_two + baselink_three + baselink_four + baselink_five + baselink_six + baselink_seven
    r = requests.get(firstlink)
    soup = BeautifulSoup(r.text, 'html.parser')
    initial_results = soup.find_all('th', attrs={'class':'ddtitle'})
    links = []
    sections = []
    for i in initial_results:
        links.append(str(i))

    for i in range(len(links)):
        index = len(links[i])-links[i][::-1].find('-')
        sections.append(links[i][index:-9])
        links[i] = links[i].split('<a')
        links[i] = links[i][1]
        links[i] = links[i].split('>')
        links[i] = links[i][0][7:-1]
        links[i] = links[i].split('amp;')
        links[i] = links[i][0] + links[i][1]
        links[i] = 'https://oscar.gatech.edu/' + links[i]
    final_results = soup.find_all('table', attrs={'class':'datadisplaytable'})
    finallinks = []
    for i in final_results:
        finallinks.append(str(i))
    finallinks = finallinks[1:-1]
    for i in range(len(finallinks)):
        finallinks[i] = finallinks[i].split('/tr')
        finallinks[i] = finallinks[i][1]
        finallinks[i] = finallinks[i].split('<td class="dddefault">')
        finallinks[i] = finallinks[i][2:]
    
    temp = []
    for i in range(len(finallinks)):
        brac = finallinks[i][-1].find('(')
        time = finallinks[i][0][:-6]
        days = finallinks[i][1][:-6]
        location = finallinks[i][2][:-6]
        professor = finallinks[i][-1][:brac]
        link = links[i]
        section = sections[i]
        crn = link[-5:]
        if '<abbr' in time:
            time = 'TBA'
        if '<abbr' in days:
            days = 'TBA'
        if '<abbr' in location:
            location = 'TBA'
        if '\xa0' in days:
            days = 'TBA'
        temp.append([section, crn, time, days, location, link, professor])

    for i in range(len(temp)):
        professor = temp[i][-1]
        professor = professor.split()
        if len(professor) > 2 and professor[-1] == 'Jr':
            x = professor[0]
            for j in range(len(1,professor)):
                x = x + ' ' + professor[j]
            professor = x
        else:
            professor = professor[0] + ' ' + professor[-1]
        if '<abbr' in professor:
            professor = 'TBA'
        temp[i][-1] = professor
        link = temp[i][-2]
        r2 = requests.get(link)
        soup1 = BeautifulSoup(r2.text, 'html.parser')
        credit = str(soup1)
        newindex = credit.find('Credits')
        hours = credit[newindex-6]
        temp[i][-2] = hours
        seats = soup1.find_all('table', attrs={'class':'datadisplaytable'})
        seatlist = str(seats[1])
        seatlist = seatlist.split('<tr>')
        seatlist = seatlist[-2]
        seatlist = seatlist.split('<td class="dddefault">')
        capacity = seatlist[-3][:-6]
        registered = seatlist[-2][:-6]
        remaining = seatlist[-1][:-12]
        temp[i].append(remaining)
        temp[i].append(registered)
        temp[i].append(capacity)
    return temp
#this function returns all the data in a list of lists
def final_data(course_symbol, course_code):
    total = []
    classes = oscar_data('08','2020', course_symbol, course_code)
    for i in range(len(classes)):
        prof = classes[i][6].split()
        firstname = prof[0]
        lastname = ''
        if len(prof) > 2 and prof[-1] == 'Jr':
            lastname = prof[-2] + ' ' + prof[-1]
        else:
            lastname = prof[-1]
        critique_data = get_grades(course_symbol + course_code, firstname, lastname)
        links = link_extractor(firstname, lastname)
        rating = data_extractor(links)
        x = classes[i] + critique_data + rating
        total.append(x)
    return total
#sorts based on rate my prof
def sort_by_rating(data):
    if len(data)>1:
        mid = len(data)//2
        lefthalf = data[:mid]
        righthalf = data[mid:]

        sort_by_rating(lefthalf)
        sort_by_rating(righthalf)
        i=j=k=0       
        while i < len(lefthalf) and j < len(righthalf):
            if lefthalf[i][-3] > righthalf[j][-3]:
                data[k]=lefthalf[i]
                i=i+1
            else:
                data[k]=righthalf[j]
                j=j+1
            k=k+1

        while i < len(lefthalf):
            data[k]=lefthalf[i]
            i=i+1
            k=k+1

        while j < len(righthalf):
            data[k]=righthalf[j]
            j=j+1
            k=k+1
    return data
#sorts based on data from critique
def sort_by_grades(data):
    if len(data)>1:
        mid = len(data)//2
        lefthalf = data[:mid]
        righthalf = data[mid:]
        sort_by_grades(lefthalf)
        sort_by_grades(righthalf)
        i=j=k=0       
        while i < len(lefthalf) and j < len(righthalf):
            if float(lefthalf[i][-5]) > float(righthalf[j][-5]):
                data[k]=lefthalf[i]
                i=i+1
            else:
                data[k]=righthalf[j]
                j=j+1
            k=k+1

        while i < len(lefthalf):
            data[k]=lefthalf[i]
            i=i+1
            k=k+1

        while j < len(righthalf):
            data[k]=righthalf[j]
            j=j+1
            k=k+1
    return data

def sort_by_pref(data, grades, rating):
    if len(data)>1:
        mid = len(data)//2
        lefthalf = data[:mid]
        righthalf = data[mid:]
        sort_by_pref(lefthalf,grades, rating)
        sort_by_pref(righthalf,grades, rating)
        i=j=k=0       
        while i < len(lefthalf) and j < len(righthalf):
            if grades * float(lefthalf[i][-5]) + rating * float(lefthalf[i][-3]) > grades * float(righthalf[j][-5]) + rating * float(righthalf[j][-3]):
                data[k]=lefthalf[i]
                i=i+1
            else:
                data[k]=righthalf[j]
                j=j+1
            k=k+1

        while i < len(lefthalf):
            data[k]=lefthalf[i]
            i=i+1
            k=k+1

        while j < len(righthalf):
            data[k]=righthalf[j]
            j=j+1
            k=k+1
    return data
    
