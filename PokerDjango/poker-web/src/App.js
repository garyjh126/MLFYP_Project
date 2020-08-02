import React, {useState, useEffect} from 'react';
import './App.css';
import Table from './components/Table.js';
import { NavigationBar } from './components/Navbar.js';

function App() {
  return (
    <div className="App"> 
      <React.Fragment>

          <NavigationBar />

          <Table />

      </React.Fragment>
    </div>
  )
}

export default App;


