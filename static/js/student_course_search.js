function search1 () {
    document.getElementById("form1").style.display = "block";
    document.getElementById("form2").style.display = "none";
    document.getElementById("form3").style.display = "none";
}
function search2 () {
    document.getElementById("form1").style.display = "none";
    document.getElementById("form2").style.display = "block";
    document.getElementById("form3").style.display = "none";
}
function search3 () {
    document.getElementById("form1").style.display = "none";
    document.getElementById("form2").style.display = "none";
    document.getElementById("form3").style.display = "block";
}
function statusSearch () {
    const content = document.getElementById("id_status");
    const value = content.options[content.selectedIndex].text;
    let searchObjectList = [];
    for (let object of objectList) {
        if (object.status === value) {
            searchObjectList.push(object);
        };
};
    placeButtons()
    loadTableData(searchObjectList);
}
function nameSearch () {
    const content = document.getElementById("id_name").value;
    if (content === "") {
        placeButtons()
        loadTableData(objectList)
    } else {
    let searchObjectList = [];
    for (let object of objectList) {
        if (object.sort_name.toUpperCase().includes(content.toUpperCase())) {
            searchObjectList.push(object);
        };
};
    placeButtons()
    loadTableData(searchObjectList);
};
    };
function categorySearch () {
    const content = document.getElementById("id_category");
    const value = content.options[content.selectedIndex].text;
    let searchObjectList = [];
    for (let object of objectList) {
        if (object.category === value) {
            searchObjectList.push(object);
         };
        };
    placeButtons()
    loadTableData(searchObjectList);
    }

document.getElementById("search1").addEventListener("click", search1);
document.getElementById("search2").addEventListener("click", search2);
document.getElementById("search3").addEventListener("click", search3);
document.getElementById("id_status").addEventListener("change", statusSearch);
document.getElementById("id_name").addEventListener("keyup", nameSearch);
document.getElementById("id_category").addEventListener("change", categorySearch);