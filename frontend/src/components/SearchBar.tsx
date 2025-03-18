import React, { useState } from 'react';

interface SearchBarProps {
    onSearch: (term: string) => void;
}

function SearchBar({ onSearch }: SearchBarProps) {
    const [searchTerm, setSearchTerm] = useState('');

    const handleSearch = () => {
        onSearch(searchTerm);
    };

    return (
        <div className="search-bar">
            <input
             type="text"
             placeholder="Поиск по вопросам..."
             value={searchTerm}
             onChange={(e) => setSearchTerm(e.target.value)}
            />
         <button onClick={handleSearch}>Найти</button>
        </div>
    );
}

export default SearchBar;