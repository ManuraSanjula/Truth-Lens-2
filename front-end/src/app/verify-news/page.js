'use client'

import {Navigation} from "@/components/Navigation";
import React, { useState, useEffect } from "react";
import {IoDocumentTextOutline, IoOpenOutline} from "react-icons/io5";
import {FooterComponent} from "@/components/Footer";
import {BiError} from "react-icons/bi";
import {IoMdCheckmarkCircleOutline} from "react-icons/io";

export default function Page(){
    const [content, setContent] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [results, setResults] = useState(null);
    const [contentId, setContentId] = useState(null);
    const [status, setStatus] = useState('idle'); // idle, submitting, checking_status, fetching_results, completed, error

    // Step 1: Submit content
    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        setStatus('submitting');
        setResults(null);
        setContentId(null);

        try {
            const formData = new FormData();
            formData.append("content_type", "text");
            formData.append("raw_text", content);
            formData.append("user_id", "6804a44d00830494ddddbafd");

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
            setError(`Failed to submit content: ${err.message}`);
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

        // If multiple results exist (due to runtime errors), show all of them
        return results.map((result, index) => {
            // Determine if content is fake or authentic
            const isFake = result.is_fake;
            const resultColor = isFake ? 'red' : 'green';
            const ResultIcon = isFake ? BiError : IoMdCheckmarkCircleOutline;

            // Format confidence as percentage
            const confidencePercentage = (result.confidence * 100).toFixed(1);

            // Format the processed date
            const processedDate = new Date(result.processed_at).toLocaleString();

            return (
                <div key={result._id || index} className={index > 0 ? 'mt-6' : ''}>
                    {results.length > 1 && (
                        <div className="mx-5 md:mx-10 mb-2">
                            <span className="text-sm text-gray-500">Result {index + 1} of {results.length}</span>
                        </div>
                    )}

                    <div id={`verify-results-${index}`} className={'mt-10'}>
                        <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Verification Results</h2>
                        <div className={'border border-zinc-300 bg-white rounded-md space-y-2 p-4 mt-4 mx-5 md:mx-10'}>
                            <h3 className={'text-gray-400 text-[13px] flex place-items-center gap-2 font-semibold'}>
                                <ResultIcon className={`text-${resultColor}-600 bg-${resultColor}-200 rounded-full w-8 h-8 p-2`} />
                                Analysis Result
                            </h3>
                            <h1 className={`text-lg text-${resultColor}-600 font-semibold`}>
                                {isFake ? 'Fake News Detected' : 'Authentic Content Verified'}
                            </h1>
                            <p className={'text-sm text-gray-400'}>
                                Our AI has determined this content is {isFake ? 'fake' : 'authentic'} with {confidencePercentage}% confidence.
                            </p>

                            {/* Additional Information */}
                            <div className={'mt-4 space-y-2'}>
                                <p className={'text-sm text-gray-600'}>
                                    <span className={'font-semibold'}>Content ID:</span> {result.content_id}
                                </p>
                                <p className={'text-sm text-gray-600'}>
                                    <span className={'font-semibold'}>Detection Type:</span> {result.detection_type.replace('_', ' ').toUpperCase()}
                                </p>
                                <p className={'text-sm text-gray-600'}>
                                    <span className={'font-semibold'}>Model Used:</span> {result.model_used}
                                </p>
                                <p className={'text-sm text-gray-600'}>
                                    <span className={'font-semibold'}>Model Version:</span> {result.model_version}
                                </p>
                                <p className={'text-sm text-gray-600'}>
                                    <span className={'font-semibold'}>Processed At:</span> {processedDate}
                                </p>
                            </div>

                            <div className={'flex gap-2 mt-4'}>
                                <button
                                    className={'bg-[#4f46e5] text-[12px] cursor-pointer font-semibold text-white px-4 py-2 rounded-md hover:bg-[#3d36b2] transition duration-200'}
                                >
                                    View Detailed Report
                                </button>
                                <button
                                    className={'bg-white text-[12px] cursor-pointer text-black border border-zinc-300 px-4 py-2 rounded-md hover:bg-[#f9fafb] transition duration-200'}
                                >
                                    Share Report
                                </button>
                            </div>
                        </div>
                    </div>

                    {result.explanation && (
                        <div id={`ai-explanation-${index}`} className={'mt-10'}>
                            <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>AI Explanation</h2>
                            <div className="border border-zinc-200 bg-white rounded-md p-5 mx-5 mt-4 md:mx-10 space-y-4">
                                <div className="space-y-2">
                                    <h3 className="text-[15px] font-semibold text-black">
                                        Analysis Details
                                    </h3>
                                    <p className="text-sm text-zinc-500 leading-relaxed text-justify">
                                        {result.explanation || 'No detailed explanation provided for this analysis.'}
                                    </p>
                                </div>
                                <div className="flex gap-3 pt-2">
                                    <button className="text-sm text-indigo-600 cursor-pointer border border-indigo-600 rounded-md px-4 py-2 hover:bg-indigo-50 transition">
                                        Share Result
                                    </button>
                                    <button className="text-sm text-red-600 cursor-pointer border border-red-600 rounded-md px-4 py-2 hover:bg-red-50 transition">
                                        Report Inaccuracy
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            );
        });
    };

    return (
        <>
            <Navigation/>
            <div className={'mt-10'}>
                <h1 className={'text-3xl font-semibold text-center'}>News verification tool to analyze content authenticity</h1>
                <div id={'verify-content'} className={'mt-10'}>
                    <h2 className={'text-xl text-black font-semibold mx-5 md:mx-10'}>Verify Content</h2>
                    <div className={'p-4 border border-zinc-300 bg-white rounded-md mx-5 md:mx-10 mt-4 space-y-4'}>
                        <h3 className={'text-base flex gap-1'}><IoDocumentTextOutline className={'text-[#4f46e5] text-xl'} />Input Content for Verification</h3>
                        <p className={'text-sm text-gray-400'}>Paste a news article, headline or upload a media to verify its authenticity</p>
                        <form onSubmit={handleSubmit}>
                            <label htmlFor={'content'} className={'text-sm text-gray-900 font-semibold'}>Content Type</label>
                            <textarea
                                name={'content'}
                                id={'content'}
                                required
                                value={content}
                                onChange={(e) => setContent(e.target.value)}
                                className={'w-full h-32 p-3 border border-zinc-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#4f46e5]'}
                                placeholder={'Paste news article, headline or URL here...'}
                                disabled={isLoading}
                            />
                            {error && (
                                <p className="mt-2 text-sm text-red-600">{error}</p>
                            )}
                            <div className={'flex mt-4'}>
                                <button
                                    type={'submit'}
                                    disabled={isLoading}
                                    className={`bg-[#4f46e5] text-[12px] cursor-pointer font-semibold text-white px-4 py-2 rounded-md transition duration-200 ${
                                        isLoading 
                                            ? 'opacity-50 cursor-not-allowed' 
                                            : 'hover:bg-[#3d36b2]'
                                    }`}
                                >
                                    {status === 'submitting' ? 'Submitting...' :
                                     status === 'checking_status' ? 'Checking Status...' :
                                     status === 'fetching_results' ? 'Fetching Results...' :
                                     'Analyze Content'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>

                {/* Show processing status */}
                {(status === 'checking_status' || status === 'fetching_results') && (
                    <div className="mt-6 mx-5 md:mx-10">
                        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
                            <div className="flex items-center">
                                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-3"></div>
                                <p className="text-sm text-blue-700">
                                    {status === 'checking_status' ? 'Checking content status...' : 'Fetching results...'}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Show results when available */}
                {status === 'completed' && results && renderResults()}

                {/* Show error if any */}
                {status === 'error' && error && (
                    <div className="mt-6 mx-5 md:mx-10">
                        <div className="bg-red-50 border border-red-200 rounded-md p-4">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                )}
            </div>
            <FooterComponent/>
        </>
    )
}