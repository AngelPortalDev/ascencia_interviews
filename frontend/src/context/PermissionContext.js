import { createContext, useContext,useState} from "react";

const PermissionContext = createContext();

export const usePermission = () => useContext(PermissionContext);

export const PermissionProvider = ({children}) =>{





    const [termsAccept, setTermsAccept] = useState(
        localStorage.getItem("termsAccepted") === "true"
    )

    const [audioVideoAccepted, setAudioVideoAccepted] = useState(
        localStorage.getItem("hasPermissions") === "true"
    )

    const[isExamSubmitted,setIsExamSubmitted] = useState(
        localStorage.getItem("InterviewSubitted") === "true");


    const acceptTerms = (zoho_lead_id)=>{
        setTermsAccept(true);
        localStorage.setItem("termsAccepted", "true");
    }

    const acceptAudioVideo = ()=>{
        setAudioVideoAccepted(true);
        localStorage.setItem("hasPermissions", "true");
    }

    const submitExam  = ()=>{
        setIsExamSubmitted(true);
        localStorage.setItem("InterviewSubitted", "true");
    }


    console.log("Context Values:", { termsAccept, audioVideoAccepted, isExamSubmitted });

    return(
       <PermissionContext.Provider value={{termsAccept,audioVideoAccepted,isExamSubmitted, acceptAudioVideo, acceptTerms, submitExam }}>
        {children}
       </PermissionContext.Provider>   
    )
}