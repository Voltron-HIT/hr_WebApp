// function to add dynamically add fields to work experience
function addWorkExperienceField(){
    var button = document.getElementById('add')
    var numberOfWorkExperiences = document.getElementById('numberOfWorkExperiences')
    var workexperience = document.getElementById('workexperience')
    var fieldNumbers = workexperience.childElementCount - 2;
    fieldNumbers += 1
    var cloneElement = workexperience.firstElementChild.cloneNode(true)
    cloneElement.className = "field added"
    cloneElement.id = "wfield" + fieldNumbers
    cloneElement.childNodes[3].value = ""
    cloneElement.childNodes[7].value = ""
    cloneElement.childNodes[11].value = ""
    cloneElement.childNodes[3].name = "organisation" + fieldNumbers
    cloneElement.childNodes[7].name = "position" + fieldNumbers
    cloneElement.childNodes[11].name = "timeframe" + fieldNumbers
    workexperience.insertBefore(cloneElement,button)
    numberOfWorkExperiences.value = fieldNumbers

}
// function to add dynamically add fields to qualifications
function addQualificationField(){
    var button = document.getElementById('addqualification')
    var qualification = document.getElementById('qualification')
    var fieldNumbers = qualification.childElementCount - 2;
    var numberOfQualifications = document.getElementById('numberOfQualifications')
    var cloneElement = qualification.firstElementChild.cloneNode(true)
    cloneElement.className = "field added"
    cloneElement.id = "qfield" + fieldNumbers
    fieldNumbers += 1
    cloneElement.childNodes[3].value = ""
    cloneElement.childNodes[7].value = ""
    cloneElement.childNodes[3].name = "qualification" + fieldNumbers
    cloneElement.childNodes[7].name = "awardingInstitute" + fieldNumbers
    qualification.insertBefore(cloneElement,button)
    numberOfQualifications.value = fieldNumbers
}
// function to remove unwanted field from work exprerience
function removeWorkExperienceField(){
    try{
        var workexperience = document.getElementById('workexperience')
        var numberOfWorkExperiences = document.getElementById('numberOfWorkExperiences')
        var fieldNumbers = workexperience.childElementCount - 2;
        var childName = 'wfield' + fieldNumbers;
        var parent = document.getElementById('workexperience')
        var child = document.getElementById(childName)
        parent.removeChild(child)
        numberOfWorkExperiences.value = fieldNumbers
    } catch(e){
        alert('There Must be At least One Field')
    }

}

function removeQualificationField(){
    try{
        var numberOfQualifications = document.getElementById('numberOfQualifications')
        var qualification = document.getElementById('qualification')
        var fieldNumbers = qualification.childElementCount - 3
        var childName = 'qfield' + fieldNumbers
        var child = document.getElementById(childName)
        qualification.removeChild(child)
        numberOfQualifications.value = fieldNumbers
    } catch(e){
        alert('There Must Be At Least One Field')
    }

}
