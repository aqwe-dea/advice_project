import React, { useState } from 'react';

interface SpoilerProps {
    title: string;
    content: string;
}

function Spoiler ({ title, content }: SpoilerProps) {
    const [expanded, setExpanded] = useState(false);

    return (
        <div className="spoiler">
            <button onClick={() => setExpanded(!expanded)}>{title}</button>
            {expanded && <div className="content">{content}</div>}
        </div>
    );
}

export default Spoiler;