function PalmReaderForm() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-red-200 p-8 rounded-lg shadow-lg max-w-md w-full">
        <h1 className="text-3xl font-bold text-center text-gray-200 mb-6">Palm Reader</h1>
        <button className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-4 rounded transition-colors">
          Start Reading
        </button>
      </div>
    </div>
  )
}

export default PalmReaderForm