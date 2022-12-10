function month_conv(date) {
    date = date.replace("Jan","stycz")
    date = date.replace("Feb.","luty")
    date = date.replace("Mar","mar")
    date = date.replace("Apr","kwiec")
    date = date.replace("May","maj")
    date = date.replace("June","czerw.")
    date = date.replace("July","lip.")
    date = date.replace("Aug","sierp")
    date = date.replace("Sept","wrzes")
    date = date.replace("Oct","pazdz")
    date = date.replace("Nov","listop")
    date = date.replace("Dec","grudz")
    date = date.replace(", midnight","")
    return date
}