import { createContext, useContext,useState,useEffect} from "react";
import { useParams } from "react-router-dom";

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
        localStorage.getItem("interviewSubmitted") === "true");



        useEffect(() => {
            if (isExamSubmitted && !sessionStorage.getItem("hasPageReloaded")) {
              sessionStorage.setItem("hasPageReloaded", "true");
              window.location.reload();
            }
          }, [isExamSubmitted]);

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
        localStorage.setItem("interviewSubmitted", "true");
        sessionStorage.setItem("isReload", "true");
        setIsExamSubmitted(true); 
        setTimeout(() => setIsExamSubmitted(localStorage.getItem("interviewSubmitted") === "true"), 100);
    }


    console.log("Context Values:", { termsAccept, audioVideoAccepted, isExamSubmitted });

    return(
       <PermissionContext.Provider value={{termsAccept,audioVideoAccepted,isExamSubmitted, acceptAudioVideo, acceptTerms, submitExam }}>
        {children}
       </PermissionContext.Provider>   
    )
}