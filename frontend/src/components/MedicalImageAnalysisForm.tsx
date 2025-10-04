import React, { useState, useRef } from 'react';
import '../App.css';

const MedicalImageAnalysisForm = () => {
  const [image, setImage] = useState<File | null>(null);
  const [patientInfo, setPatientInfo] = useState({
    age: '',
    gender: 'не указан',
    symptoms: '',
    medical_history: '',
    imaging_type: 'рентген'
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);
  const [progress, setProgress] = useState(0);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedImage = e.target.files[0];
      const allowedExtensions = ['.jpg', '.jpeg', '.png', '.dcm'];
      const fileExt = selectedImage.name.toLowerCase().split('.').pop();
      if (!fileExt || !allowedExtensions.includes(`.${fileExt}`)) {
        setError(`Поддерживаются только форматы: ${allowedExtensions.join(', ')}`);
        if (imageInputRef.current) {
          imageInputRef.current.value = '';
        }
        return;
      }
      setImage(selectedImage);
      setError(null);
    }
  };
  const handlePatientInfoChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setPatientInfo(prev => ({ ...prev, [name]: value }));
  };
  const handleAnalyze = async () => {
    if (!image) {
      setError('Пожалуйста, загрузите изображение');
      return;
    }
    if (!patientInfo.symptoms.trim()) {
      setError('Пожалуйста, укажите симптомы');
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
      formData.append('image', image);
      formData.append('age', patientInfo.age);
      formData.append('gender', patientInfo.gender);
      formData.append('symptoms', patientInfo.symptoms);
      formData.append('medical_history', patientInfo.medical_history);
      formData.append('imaging_type', patientInfo.imaging_type);
      const response = await fetch('https://advice-project.onrender.com/medical-image-analysis/', {
        method: 'POST',
        body: formData
      });
      clearInterval(progressInterval);
      setProgress(100);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Ошибка при медицинском анализе');
      }
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при медицинском анализе');
    } finally {
      setIsLoading(false);
    }
  };
  const renderMedicalAnalysis = () => {
    if (!result || !result.medical_analysis) return null;
    const sections = {
      interpretation: extractSection(result.medical_analysis, "1.", "2."),
      diagnostic: extractSection(result.medical_analysis, "2.", "3."),
      diagnoses: extractSection(result.medical_analysis, "3.", "4."),
      treatment: extractSection(result.medical_analysis, "4.", "5."),
      monitoring: extractSection(result.medical_analysis, "5.", "6."),
      prognosis: extractSection(result.medical_analysis, "6.", "7."),
      lifestyle: extractSection(result.medical_analysis, "7.", null)
    };
    return (
      <div className="medical-analysis">
        <h3>Медицинский анализ: {result.patient_info.imaging_type}</h3>
        <div className="section">
          <h4>1. Интерпретация результатов</h4>
          <div className="section-content">{sections.interpretation || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>2. Диагностические рекомендации</h4>
          <div className="section-content">{sections.diagnostic || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>3. Возможные диагнозы</h4>
          <div className="section-content">{sections.diagnoses || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>4. Рекомендации по лечению</h4>
          <div className="section-content">{sections.treatment || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>5. Рекомендации по наблюдению</h4>
          <div className="section-content">{sections.monitoring || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>6. Прогноз</h4>
          <div className="section-content">{sections.prognosis || "Не найдено"}</div>
        </div>
        <div className="section">
          <h4>7. Рекомендации по образу жизни</h4>
          <div className="section-content">{sections.lifestyle || "Не найдено"}</div>
        </div>
        <button 
          onClick={() => setResult(null)}
          className="reset-button"
        >
          Провести новый анализ
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
    <div className="medical-analysis-container">
      <h2>Медицинский анализ изображений</h2>
      <p>Загрузите медицинское изображение (рентген, УЗИ, МРТ, КТ) для профессионального анализа</p>
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      <div className="form-section">
        <div className="form-group">
          <label htmlFor="image">Медицинское изображение *</label>
          <input
            type="file"
            id="image"
            accept=".jpg,.jpeg,.png,.dcm"
            onChange={handleImageChange}
            ref={imageInputRef}
            disabled={isLoading}
          />
          {image && (
            <div className="file-info">
              <span>Выбрано изображение: {image.name}</span>
              <button 
                onClick={() => {
                  setImage(null);
                  if (imageInputRef.current) {
                    imageInputRef.current.value = '';
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
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="age">Возраст</label>
            <input
              type="text"
              id="age"
              name="age"
              value={patientInfo.age}
              onChange={handlePatientInfoChange}
              placeholder="Например: 45"
              disabled={isLoading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="gender">Пол</label>
            <select
              id="gender"
              name="gender"
              value={patientInfo.gender}
              onChange={handlePatientInfoChange}
              disabled={isLoading}
            >
              <option value="не указан">Не указан</option>
              <option value="мужской">Мужской</option>
              <option value="женский">Женский</option>
            </select>
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="imaging_type">Тип изображения</label>
          <select
            id="imaging_type"
            name="imaging_type"
            value={patientInfo.imaging_type}
            onChange={handlePatientInfoChange}
            disabled={isLoading}
          >
            <option value="рентген">Рентген</option>
            <option value="УЗИ">УЗИ</option>
            <option value="МРТ">МРТ</option>
            <option value="КТ">КТ</option>
            <option value="другое">Другое</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="symptoms">Симптомы *</label>
          <textarea
            id="symptoms"
            name="symptoms"
            value={patientInfo.symptoms}
            onChange={handlePatientInfoChange}
            placeholder="Опишите симптомы пациента"
            rows={4}
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="medical_history">Медицинская история</label>
          <textarea
            id="medical_history"
            name="medical_history"
            value={patientInfo.medical_history}
            onChange={handlePatientInfoChange}
            placeholder="Укажите хронические заболевания, аллергии, принимаемые лекарства"
            rows={3}
            disabled={isLoading}
          />
        </div>
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
            {progress < 30 ? 'Анализируем изображение...' : 
             progress < 60 ? 'Интерпретируем результаты...' :
             progress < 90 ? 'Формируем рекомендации...' : 'Готовим окончательный анализ...'}
          </p>
        </div>
      )}
      {result ? (
        renderMedicalAnalysis()
      ) : (
        <button 
          onClick={handleAnalyze} 
          disabled={isLoading || !image || !patientInfo.symptoms.trim()}
          className="analyze-button"
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Проводим медицинский анализ...
            </>
          ) : (
            'Провести анализ'
          )}
        </button>
      )}
      <div className="footer-note">
        Советница АКВИ проводит анализ медицинских изображений с использованием передовых моделей искусственного интеллекта. 
        Результаты носят рекомендательный характер и не заменяют консультацию квалифицированного врача.
      </div>
    </div>
  );
};

export default MedicalImageAnalysisForm;