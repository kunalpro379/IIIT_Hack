import React, { useState } from 'react';
import { X, Upload, AlertCircle, MapPin } from 'lucide-react';
import { translations } from '../translations';

interface GrievanceFormProps {
  isAnonymous: boolean;
  onClose: () => void;
  language: 'en' | 'hi';
}

const GrievanceForm: React.FC<GrievanceFormProps> = ({ isAnonymous, onClose, language }) => {
  const t = translations[language];
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: '',
    district: '',
    tehsil: '',
    ward: '',
    pincode: '',
    name: '',
    email: '',
    phone: '',
  });

  const [files, setFiles] = useState<File[]>([]);
  const [aiSuggestions, setAiSuggestions] = useState<string[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const description = e.target.value;
    setFormData({ ...formData, description });

    if (description.toLowerCase().includes('water')) {
      setAiSuggestions([
        'Similar water-related grievances found in your area',
        'Suggested category: Water Supply',
        'High priority issue detected',
      ]);
    } else if (description.toLowerCase().includes('road')) {
      setAiSuggestions([
        'Multiple road maintenance issues reported nearby',
        'Suggested category: Infrastructure',
        'Medium priority issue detected',
      ]);
    } else {
      setAiSuggestions([]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log({ ...formData, files });
    onClose();
  };

  return (
    <div className="backdrop-blur-md text-gray-100">
      <div className="flex justify-between items-center mb-6 p-6 border-b border-white/10">
        <h2 className="text-2xl font-bold">{t.submitGrievance}</h2>
        <button onClick={onClose} className="text-gray-300 hover:text-white">
          <X className="h-6 w-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6 p-6">
        {!isAnonymous && (
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">{t.name}</label>
              <input
                type="text"
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
                required={!isAnonymous}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">{t.email}</label>
              <input
                type="email"
                className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
                required={!isAnonymous}
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">{t.grievanceTitle}</label>
          <input
            type="text"
            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
            required
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-1">{t.description}</label>
          <textarea
            className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400 h-32"
            required
            value={formData.description}
            onChange={handleDescriptionChange}
          />
          {aiSuggestions.length > 0 && (
            <div className="mt-2 p-3 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-800 mb-2">AI Suggestions:</p>
              <ul className="text-sm text-blue-700 space-y-1">
                {aiSuggestions.map((suggestion, index) => (
                  <li key={index} className="flex items-center">
                    <span className="w-2 h-2 bg-blue-400 rounded-full mr-2"></span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{t.category}</label>
            <select
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
              required
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            >
              <option value="">{t.selectCategory}</option>
              <option value="water">Water Supply</option>
              <option value="electricity">Electricity</option>
              <option value="roads">Roads</option>
              <option value="sanitation">Sanitation</option>
              <option value="healthcare">Healthcare</option>
              <option value="education">Education</option>
              <option value="other">Other</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{t.district}</label>
            <input
              type="text"
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
              required
              value={formData.district}
              onChange={(e) => setFormData({ ...formData, district: e.target.value })}
            />
          </div>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{t.tehsil}</label>
            <input
              type="text"
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
              required
              value={formData.tehsil}
              onChange={(e) => setFormData({ ...formData, tehsil: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{t.ward}</label>
            <input
              type="text"
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
              required
              value={formData.ward}
              onChange={(e) => setFormData({ ...formData, ward: e.target.value })}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">{t.pincode}</label>
            <input
              type="text"
              pattern="[0-9]{6}"
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#FFA41B] text-white placeholder-gray-400"
              required
              value={formData.pincode} onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
            />
          </div>
        </div>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
          <div className="flex flex-col items-center">
            <Upload className="h-8 w-8 text-gray-400 mb-2" />
            <p className="text-sm text-gray-600 mb-1">{t.uploadInstructions}</p>
            <input
              type="file"
              id="file-upload"
              multiple
              className="hidden"
              onChange={handleFileChange}
              accept="image/*,video/*,.pdf"
            />
            <label
              htmlFor="file-upload"
              className="bg-indigo-50 text-indigo-600 px-4 py-2 rounded-lg cursor-pointer hover:bg-indigo-100 transition-colors"
            >
              {t.chooseFiles}
            </label>
            {files.length > 0 && (
              <div className="mt-4 w-full">
                <p className="text-sm font-medium text-gray-700 mb-2">Selected files:</p>
                <ul className="space-y-2">
                  {files.map((file, index) => (
                    <li key={index} className="text-sm text-gray-600 flex items-center">
                      <span className="w-2 h-2 bg-indigo-400 rounded-full mr-2"></span>
                      {file.name}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>

        {isAnonymous && (
          <div className="flex items-start p-4 bg-yellow-50 rounded-lg">
            <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5 mr-3 flex-shrink-0" />
            <p className="text-sm text-yellow-700">{t.anonymousDisclaimer}</p>
          </div>
        )}

        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            {t.cancel}
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-500 transition-colors"
          >
            {t.submit}
          </button>
        </div>
      </form>
    </div>
  );
};

export default GrievanceForm;