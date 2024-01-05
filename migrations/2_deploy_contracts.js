const DTindexing = artifacts.require("DTindexing");
const DTmonitoringOracle = artifacts.require("DTmonitoringOracle");

module.exports = function (deployer) {
  let DTmonitoringOracleInstance;

  deployer.deploy(DTmonitoringOracle)
    .then((instance) => {
      DTmonitoringOracleInstance = instance;
      console.log("DTmonitoringOracle address:", instance.address);
      return deployer.deploy(DTindexing, DTmonitoringOracleInstance.address);
    }).then((DTindexingInstance) => {
      console.log("DTindexing address:", DTindexingInstance.address);
    });
};