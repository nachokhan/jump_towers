import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);

  const onFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const onFileUpload = () => {
    const formData = new FormData();
    formData.append('file', file);
    axios.post("http://localhost:8000/upload", formData, {
    }).then(response => {
      console.log(response.data);
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <input type="file" onChange={onFileChange} />
        <button onClick={onFileUpload}>
          Upload!
        </button>
      </header>
    </div>
  );
}

export default App;