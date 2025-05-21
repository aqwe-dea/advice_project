
interface HuggingFaceResponse {
    response: string;
}

const response = await axios.post<HuggingFaceResponse>('/chat/', { message: input });