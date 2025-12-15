const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
if (!API_BASE_URL) {
  throw new Error("API_BASE_URL is not defined");
}

export const uploadReceipt = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/v1/bills/ocr`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("OCR request failed");
  }

  return await response.json();
};

export const calculateSplit = async (bills) => {
  const response = await fetch(`${API_BASE_URL}/api/v1/bills/split`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ bills }),
  });

  if (!response.ok) {
    throw new Error("Split calculation failed");
  }

  return await response.json();
};
