let sortDirection = false;

  function sortColumn(columnName) {
      const dataType = typeof objectList[0][columnName];
      sortDirection = !sortDirection;
      switch(dataType) {
        case 'number':
            sortNumberColumn(sortDirection, columnName);
            break;
        case 'string':
            sortStringColumn(sortDirection,"sort_" + columnName);
      };
      loadTableData(objectList);
    };

    function sortNumberColumn(sort, columnName) {
      objectList = objectList.sort((p1,p2) => {
        return sort ? p1[columnName] - p2[columnName] : p2[columnName] - p1[columnName]
      })
    };

    function sortStringColumn(sort, columnName) {
      const sortDataType = typeof objectList[0][columnName]
      switch(sortDataType) {
        case 'string':
          objectList = objectList.sort((p1,p2) => {
            return sort ? (p1[columnName].localeCompare(p2[columnName])) : (p2[columnName].localeCompare(p1[columnName]))
          });
          break;
        case 'object':
          return sortNumberColumn(sort, columnName);
      }
    }

  window.onload = () => {
    loadTableData(objectList)
  };