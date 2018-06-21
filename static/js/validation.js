function validateDOB( dob ){
    dob = dob.replace(/-/g,'/')
    dob = new Date(dob)
    let dateToday = new Date()
    
    years = Math.abs(dob.getFullYear()-dateToday.getFullYear())
    if( years > 0 && years < 80){
        return true
    } else {
        return false
    }
}

function validateFile( filename ){
    if ( fileExtension( filename ) === 'pdf' || fileExtension( filename ) === 'docx' || fileExtension( filename ) === 'doc' ){
        return true
    } else {
        return false
    }
}

function fileExtension( filename ){
    return filename.split('.').pop();
}