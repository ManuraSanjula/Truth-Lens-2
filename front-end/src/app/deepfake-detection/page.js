'use client'

import {Navigation} from "@/components/Navigation";
import React, { useState } from "react";
import {FileInput, Label} from "flowbite-react";
import {BiError} from "react-icons/bi";
import {FooterComponent} from "@/components/Footer";
import {IoMdCheckmarkCircleOutline} from "react-icons/io";

export default function Page(){
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [results, setResults] = useState(null);
    const [contentId, setContentId] = useState(null);
    const [status, setStatus] = useState('idle'); // idle, submitting, checking_status, fetching_results, completed, error
    const [fileName, setFileName] = useState('');

    // Handle file selection
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setFileName(selectedFile.name);
            setError('');
        }
    };

    // Step 1: Submit file
    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!file) {
            setError('Please select a file to analyze');
            return;
        }

        setIsLoading(true);
        setError('');
        setStatus('submitting');
        setResults(null);
        setContentId(null);

        try {
            const formData = new FormData();
            formData.append("content_type", "image");
            formData.append("user_id", "6804a44d00830494ddddbafd");
            formData.append("file", file);

            const response = await fetch('http://localhost:8000/api/v1/content/submit', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // Check if content_id exists in response
            if (!data.content_id) {
                throw new Error('No content_id received from server');
            }

            console.log('Received content_id:', data.content_id);
            setContentId(data.content_id);
            setStatus('checking_status');
            // Proceed to check status
            checkContentStatus(data.content_id);

        } catch (err) {
            setError(`Failed to submit file: ${err.message}`);
            setStatus('error');
            setIsLoading(false);
            console.error('Submit Error:', err);
        }
    };

    // Step 2: Check content status
    const checkContentStatus = async (id) => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/content/status/${id}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Status check response:', data);

            // Check if the content is completed
            if (data.status === 'completed') {
                setStatus('fetching_results');
                fetchResults(id);
            } else if (data.status === 'processing' || data.status === 'pending') {
                // If still processing, check again after delay
                setTimeout(() => checkContentStatus(id), 2000);
            } else {
                // Any other status is considered an error
                throw new Error(`Unexpected status: ${data.status}`);
            }

        } catch (err) {
            setError(`Failed to check status: ${err.message}`);
            setStatus('error');
            setIsLoading(false);
            console.error('Status Check Error:', err);
        }
    };

    // Step 3: Fetch results
    const fetchResults = async (id) => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/results/content/${id}`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Results response:', data);

            // Check if results exist and is an array
            if (!Array.isArray(data) || data.length === 0) {
                throw new Error('No results found for this content');
            }

            // Verify content_id matches in all results
            const invalidResults = data.filter(result => result.content_id !== id);
            if (invalidResults.length > 0) {
                throw new Error('Content ID mismatch in results');
            }

            setResults(data);
            setStatus('completed');
            setIsLoading(false);

        } catch (err) {
            setError(`Failed to fetch results: ${err.message}`);
            setStatus('error');
            setIsLoading(false);
            console.error('Results Fetch Error:', err);
        }
    };

    const renderResults = () => {
        if (!results || !Array.isArray(results) || results.length === 0) return null;

        return results.map((result, index) => {
            // For deepfake detection, we'll use the confidence and is_fake fields
            const isManipulated = result.is_fake;
            const resultColor = isManipulated ? 'red' : 'green';
            const ResultIcon = isManipulated ? BiError : IoMdCheckmarkCircleOutline;

            // Format confidence as percentage
            const confidencePercentage = (result.confidence * 100).toFixed(0);

            return (
                <div key={result._id || index} className={index > 0 ? 'mt-6' : ''}>
                    {results.length > 1 && (
                        <div className="mb-2">
                            <span className="text-sm text-gray-500">Result {index + 1} of {results.length}</span>
                        </div>
                    )}

                    <h3 className={'text-lg text-black font-semibold'}>Analysis Result</h3>
                    <div className={`bg-${isManipulated ? '[#fef2f2]' : '[#f0fdf4]'} rounded-md p-4 space-y-3`}>
                        <h3 className={`text-${resultColor}-600 text-base flex gap-1 place-items-center font-semibold`}>
                            <ResultIcon className={`text-${resultColor}-600 text-xl`} />
                            {isManipulated ? `${confidencePercentage}% Likely Manipulated` : `${confidencePercentage}% Likely Authentic`}
                        </h3>
                        <p className={`text-sm text-${resultColor}-600`}>
                            {isManipulated
                                ? 'Our analysis detected significant indicators of AI manipulation in this media.'
                                : 'Our analysis suggests this media is likely authentic with no significant manipulation detected.'}
                        </p>
                    </div>

                    <div className={'grid grid-cols-1 md:grid-cols-2 gap-3 mt-4'}>
                        <div className={'bg-[#f9fafb] p-4'}>
                            <h4 className={'text-sm font-semibold'}>Analysis Details</h4>
                            <ul className={'text-sm text-zinc-700 mt-4'}>
                                <li className={'flex justify-between'}>
                                    <span>Detection Type</span>
                                    <span>{result.detection_type.replace('_', ' ').toUpperCase()}</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Confidence</span>
                                    <span>{confidencePercentage}%</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Model</span>
                                    <span>{result.model_used}</span>
                                </li>
                                <li className={'flex justify-between'}>
                                    <span>Version</span>
                                    <span>{result.model_version}</span>
                                </li>
                            </ul>
                        </div>

                        <div className={'bg-[#f9fafb] p-4'}>
                            <h4 className={'text-sm font-semibold'}>Detection Method</h4>
                            <ul className={'text-sm text-zinc-700 mt-4 list-disc ml-4'}>
                                <li>Neural Network Analysis</li>
                                <li>Pixel-level Inconsistency Detection</li>
                                <li>Digital Fingerprint Analysis</li>
                                <li>Metadata Examination</li>
                            </ul>
                        </div>
                    </div>

                    {result.explanation && (
                        <div className={'mt-4'}>
                            <h4 className={'text-sm font-semibold'}>Detailed Explanation</h4>
                            <p className={'text-sm text-zinc-600 mt-2'}>{result.explanation}</p>
                        </div>
                    )}
                </div>
            );
        });
    };

    return(
        <>
            <Navigation/>
            <div className={'my-10'}>
                <h1 className={'text-3xl font-semibold text-center'}>Deepfake Detection</h1>
                <p className={'text-gray-400 text-center text-base'}>Upload an image or video to analyze for potential AI-generated or manipulated media</p>
                <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-10 space-y-4'}>
                    <h2 className={'text-xl text-black font-semibold'}>Upload Media</h2>
                    <form onSubmit={handleSubmit}>
                        <div className="flex w-full items-center justify-center">
                            <Label
                                htmlFor="dropzone-file"
                                className="flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed
                                border-gray-300 bg-gray-50 hover:bg-gray-100 dark:border-gray-600
                                dark:hover:border-gray-500"
                            >
                                <div className="flex flex-col items-center justify-center pb-6 pt-5">
                                    <svg
                                        className="mb-4 h-8 w-8 text-gray-500 dark:text-gray-400"
                                        aria-hidden="true"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 20 16"
                                    >
                                        <path
                                            stroke="currentColor"
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth="2"
                                            d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                                        />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                        <span className="font-semibold">Click to upload</span> or drag and drop
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">PNG, JPG, GIF or VIDEO (MAX. 100MB)</p>
                                    {fileName && (
                                        <p className="mt-2 text-sm text-blue-600">Selected: {fileName}</p>
                                    )}
                                </div>
                                <FileInput
                                    id="dropzone-file"
                                    className="hidden"
                                    onChange={handleFileChange}
                                    accept="image/*,video/*"
                                />
                            </Label>
                        </div>
                        {error && (
                            <p className="mt-2 text-sm text-red-600">{error}</p>
                        )}
                        <button
                            type={'submit'}
                            disabled={isLoading}
                            className={`bg-[#4f46e5] mt-4 text-sm cursor-pointer font-semibold text-white px-4 py-2 rounded-md transition duration-200 ${
                                isLoading 
                                    ? 'opacity-50 cursor-not-allowed' 
                                    : 'hover:bg-[#3d36b2]'
                            }`}
                        >
                            {status === 'submitting' ? 'Submitting...' :
                             status === 'checking_status' ? 'Analyzing Media...' :
                             status === 'fetching_results' ? 'Fetching Results...' :
                             'Analyze Media'}
                        </button>
                    </form>

                    {/* Show processing status */}
                    {(status === 'checking_status' || status === 'fetching_results') && (
                        <div className="mt-6">
                            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                                <div className="flex items-center">
                                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                                    <p className="text-sm text-blue-700">
                                        {status === 'checking_status' ? 'Analyzing media... This may take a few moments.' : 'Fetching results...'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Display results */}
                    {status === 'completed' && results && (
                        <>
                            <hr className={'text-zinc-300 mx-20 my-10 rounded-4xl'}/>
                            {renderResults()}
                        </>
                    )}

                    {/* Show error if any */}
                    {status === 'error' && error && (
                        <div className="mt-6">
                            <div className="bg-red-50 border border-red-200 rounded-md p-4">
                                <p className="text-sm text-red-700">{error}</p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
            <FooterComponent/>
        </>
    )
}