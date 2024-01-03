pragma solidity ^0.8.20;

import {DiamondHookFutures} from "../../src/DiamondHookFutures.sol";

import {BaseHook} from "@uniswap/v4-periphery/contracts/BaseHook.sol";
import {IPoolManager} from "@uniswap/v4-core/src/interfaces/IPoolManager.sol";
import {Hooks} from "@uniswap/v4-core/src/libraries/Hooks.sol";

contract DiamondHookImpl is DiamondHookFutures {
    constructor(
        IPoolManager poolManager,
        DiamondHookFutures addressToEtch,
        int24 tickSpacing,
        uint24 baseBeta,
        uint24 decayRate,
        uint24 vaultRedepositRate
    ) DiamondHookFutures(poolManager, tickSpacing, baseBeta, decayRate, vaultRedepositRate) {
        Hooks.validateHookAddress(addressToEtch, getHooksCalls());
    }

    // make this a no-op in testing
    function validateHookAddress(BaseHook _this) internal pure override {}
}
