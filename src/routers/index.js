'use strict'

const express = require('express')
const router = express.Router()

//signUp
router.post('/v1/api', require('./access'))

module.exports = router
