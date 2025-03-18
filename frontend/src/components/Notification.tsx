import React from 'react';
import { motion } from 'framer-motion';

interface NotificationProps {
    message: string;
    onClose: () => void;
}

function Notification({ message, onClose }: {message: string; onClose: () =>void }) {
    return (
        <motion.div 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '1rem',
            backgroundColor: '#4CAF50',
            color: 'white',
            borderRadius: '4px',
            zIndex: 1000,
        }}
    >
            {message}
            <button onClick={onClose} style={{ marginLeft: '1rem'}}>Закрыть</button>
        </motion.div>
    );
}

export default Notification;