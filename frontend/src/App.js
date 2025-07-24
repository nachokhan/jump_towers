import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState([]);
  const [filter, setFilter] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 15;

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const onFileUpload = () => {
    const formData = new FormData();
    formData.append('file', file);

    axios.post("http://localhost:8000/process", formData)
      .then(response => {
        setResult(response.data.sync_result);
        setCurrentPage(1); // reset page
      })
      .catch(error => {
        console.error("Upload error", error);
      });
  };

  const exportCSV = (rows) => {
    if (rows.length === 0) return;

    const headers = Object.keys(rows[0]);
    const csvContent = [
      headers.join(","),
      ...rows.map(row => headers.map(h => row[h]).join(","))
    ].join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url;
    a.download = "filtered_result.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredResults = result.filter(row => {
    if (!filter) return true;
    return row.start_time.startsWith(filter);
  });

  const totalPages = Math.ceil(filteredResults.length / rowsPerPage);
  const paginatedResults = filteredResults.slice(
    (currentPage - 1) * rowsPerPage,
    currentPage * rowsPerPage
  );

  return (
    <div className="App">
      <h2>CSV Processor</h2>

      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>Upload</button>

      <br />

      <input
        type="date"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      <button onClick={() => exportCSV(filteredResults)}>Export to CSV</button>

      <br />

      <table>
        <thead>
          <tr>
            <th>Start Time</th>
            <th>End Time</th>
            <th>State</th>
            <th>Tower Jump</th>
            <th>Confidence</th>
          </tr>
        </thead>
        <tbody>
          {paginatedResults.map((row, index) => (
            <tr key={index}>
              <td>{row.start_time}</td>
              <td>{row.end_time}</td>
              <td>{row.State}</td>
              <td>{row.tower_jump}</td>
              <td>{row.confidence}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {filteredResults.length > 0 && (
        <div className="pagination">
          <button disabled={currentPage === 1} onClick={() => setCurrentPage(p => p - 1)}>Prev</button>
          <span>Page {currentPage} of {totalPages}</span>
          <button disabled={currentPage === totalPages} onClick={() => setCurrentPage(p => p + 1)}>Next</button>
        </div>
      )}
    </div>
  );
}

export default App;
