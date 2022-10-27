function loadData(courseList) {
    const listBody = document.getElementById("courses");
    let dataHtml = ""
    for (let course of courseList) {
      dataHtml += course
    };
    listBody.innerHTML = dataHtml;
  };
  window.onload = () => {
    loadData(courseList)
  };
  function nameSearch () {
    const content = document.getElementById("id_name").value;
    if (content === "") {
        loadData(courseList)
    } else {
    let searchObjectList = [];
    for (let object of courseList) {
        if (object.toUpperCase().includes(content.toUpperCase())) {
            searchObjectList.push(object);
        };
};
    loadData(searchObjectList);
};
    };
  document.getElementById("id_name").addEventListener("change", nameSearch);