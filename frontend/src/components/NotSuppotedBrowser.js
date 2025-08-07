import Logo from '../assest/Logo.png';

const NotSuppotedBrowser = () => {
  return (
    <>

    <div style={{ padding: "10px 20px" }}>
            <div className="logomobile">
              <img src={Logo} alt="AI Software" className="h-16" />
            </div>
            <section className="dots-container">
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  padding: "10px",
                }}
              >
                <div>
                  <h3 className="text-lg sm:text-xl font-semibold text-gray-800 text-center">
                    This browser is not supported.
                  </h3>
                  <p className="w-full text-center mt-2">
                    Please open this site in Chrome, Firefox, or another modern browser.
                  </p>
                </div>
                <br />
              </div>
            </section>
          </div>
    </>
  );
};
export default NotSuppotedBrowser;
