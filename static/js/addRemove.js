// function to add dynamically add fields to work experience
function addWorkExperienceField(){
    var button = document.getElementById('add')
    var workexperience = document.getElementById('workexperience')
    var fieldNumbers = workexperience.childElementCount - 2;
    fieldNumbers += 1
    var cloneElement = workexperience.firstElementChild.cloneNode(true)
    cloneElement.className = "field added"
    cloneElement.id = "wfield" + fieldNumbers
    cloneElement.childNodes[3].value = ""
    cloneElement.childNodes[7].value = ""
    cloneElement.childNodes[11].value = ""
    cloneElement.childNodes[3].id = "organisation" + fieldNumbers
    cloneElement.childNodes[7].id = "position" + fieldNumbers
    cloneElement.childNodes[11].id = "timeframe" + fieldNumbers
    workexperience.insertBefore(cloneElement,button)

}
// function to add dynamically add fields to qualifications
function addQualificationField(){
    var button = document.getElementById('addqualification')
    var qualification = document.getElementById('qualification')
    var fieldNumbers = qualification.childElementCount - 2;
    var cloneElement = qualification.firstElementChild.cloneNode(true)
    cloneElement.className = "field added"
    cloneElement.id = "qfield" + fieldNumbers
    fieldNumbers += 1
    cloneElement.childNodes[3].value = ""
    cloneElement.childNodes[7].value = ""
    cloneElement.childNodes[11].value = ""
    cloneElement.childNodes[3].id = "qualification" + fieldNumbers
    cloneElement.childNodes[7].id = "awardingInstitute" + fieldNumbers
    cloneElement.childNodes[11].id = "certificate" + fieldNumbers
    qualification.insertBefore(cloneElement,button)
}
// function to remove unwanted field from work exprerience
function removeWorkExperienceField(){
    try{
        var workexperience = document.getElementById('workexperience')
        var fieldNumbers = workexperience.childElementCount - 2;
        var childName = 'wfield' + fieldNumbers;
        var parent = document.getElementById('workexperience')
        var child = document.getElementById(childName)
        parent.removeChild(child)
    } catch(e){
        alert('There Must be At least One Field')
    }

}

function removeQualificationField(){
    try{
        var qualification = document.getElementById('qualification')
        var fieldNumbers = qualification.childElementCount - 3
        var childName = 'qfield' + fieldNumbers
        var child = document.getElementById(childName)
        qualification.removeChild(child)
    } catch(e){
        alert('There Must Be At Least One Field')
    }

}