import axios from 'axios';

interface HuggingFaceResponse {
    response: string;
    message: string;
}
export const sendChatMessage = async (input: string) => {
    const response = await axios.post<HuggingFaceResponse>('/chat/', { message: input });
    return response.data;
};