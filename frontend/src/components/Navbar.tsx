import React from 'react';
import { Link } from 'react-router-dom';
import { faHome, faInfoCircle, faAnkh } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

function Navbar() {
  return (
    <nav className="navbar">
      <ul>
       <li><Link to="/"><FontAwesomeIcon icon={faHome} />Главная</Link></li>
       <li><Link to="/about"><FontAwesomeIcon icon={faInfoCircle} />О проекте</Link></li>
       <li><Link to="/sovet"><FontAwesomeIcon icon={faAnkh} />Совет АКВИ</Link></li>
      </ul>
    </nav>
  );
  
}

export default Navbar;