import React, { useState, useRef } from 'react';
import '../App.css';

const LegalDocumentAnalysisForm = () => {
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (!selectedFile.name.toLowerCase().endsWith('.pdf')) {
        setError('Поддерживаются только PDF-файлы');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('Файл слишком большой. Максимальный размер: 10MB');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };
  const handleAnalyze = async () => {
    if (!file) {
      setError('Пожалуйста, выберите PDF-файл');
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    setProgress(0);
    try {
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 5;
        });
      }, 300);
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/legal-document-analysis/', {
        method: 'POST',
        body: formData
      });
      clearInterval(progressInterval);
      setProgress(100);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при анализе документа');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при анализе документа');
    } finally {
      setIsLoading(false);
    }
  };
  const renderAnalysisResults = () => {
    if (!result || !result.analysis) return null;
    const analysis = result.analysis;
    const sections = {
      risks: extractSection(analysis, "1.", "2."),
      compliance: extractSection(analysis, "2.", "3."),
      violations: extractSection(analysis, "3.", "4."),
      revisions: extractSection(analysis, "4.", "5."),
      caseLaw: extractSection(analysis, "5.", "6."),
      summary: extractSection(analysis, "6.", null)
    };
    return (
      <div className="analysis-results">
        <h3>Результаты юридического анализа</h3>
        <div className="analysis-section">
          <h4>1. Выявление ключевых рисков и уязвимостей в документе</h4>
          <div className="section-content">{sections.risks || "Не найдено"}</div>
        </div>
        <div className="analysis-section">
          <h4>2. Проверка соответствия документа Гражданскому кодексу РФ</h4>
          <div className="section-content">{sections.compliance || "Не найдено"}</div>
        </div>
        <div className="analysis-section">
          <h4>3. Определение потенциальных нарушений законодательства</h4>
          <div className="section-content">{sections.violations || "Не найдено"}</div>
        </div>
        <div className="analysis-section">
          <h4>4. Предложение конкретных правок для минимизации юридических рисков</h4>
          <div className="section-content">{sections.revisions || "Не найдено"}</div>
        </div>
        <div className="analysis-section">
          <h4>5. Сравнение с судебной практикой по аналогичным делам</h4>
          <div className="section-content">{sections.caseLaw || "Не найдено"}</div>
        </div>
        <div className="analysis-section">
          <h4>6. Формирование структурированного отчета с рекомендациями</h4>
          <div className="section-content">{sections.summary || "Не найдено"}</div>
        </div>
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Проанализировать другой документ
        </button>
      </div>
    );
  };
  const extractSection = (text: string, startMarker: string, endMarker: string | null): string => {
    const startIndex = text.indexOf(startMarker);
    if (startIndex === -1) return "";
    let endIndex = -1;
    if (endMarker) {
      endIndex = text.indexOf(endMarker, startIndex + startMarker.length);
    }
    if (endIndex === -1) {
      return text.substring(startIndex + startMarker.length).trim();
    }
    return text.substring(startIndex + startMarker.length, endIndex).trim();
  };
  return (
    <div className="legal-analysis-container">
      <h2>Юридический анализ документов</h2>
      <p>Загрузите PDF-документ для автоматического анализа на юридические риски</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      <div className="file-upload-section">
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileChange}
          ref={fileInputRef}
          disabled={isLoading}
        />
        {file && (
          <div className="file-info">
            <span>Выбран файл: {file.name}</span>
            <button 
              onClick={() => {
                setFile(null);
                if (fileInputRef.current) {
                  fileInputRef.current.value = '';
                }
              }}
              disabled={isLoading}
              className="remove-file-button"
            >
              Удалить
            </button>
          </div>
        )}
      </div>
      {isLoading && (
        <div className="progress-section">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <p className="progress-text">
            {progress < 30 ? 'Анализируем документ...' : 
             progress < 60 ? 'Идентифицируем риски...' :
             progress < 90 ? 'Формируем рекомендации...' : 'Готовим результаты...'}
          </p>
        </div>
      )}
      {result ? (
        renderAnalysisResults()
      ) : (
        <button 
          onClick={handleAnalyze} 
          disabled={isLoading || !file}
          className="analyze-button"
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Анализируем документ...
            </>
          ) : (
            'Анализировать документ'
          )}
        </button>
      )}
      <div className="footer-note">
        Советница АКВИ анализирует документы с использованием передовых моделей искусственного интеллекта 
        и проверенных юридических практик. Результаты носят рекомендательный характер.
      </div>
    </div>
  );
};

export default LegalDocumentAnalysisForm;