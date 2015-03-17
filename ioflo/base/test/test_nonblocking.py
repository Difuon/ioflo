# -*- coding: utf-8 -*-
"""
Unittests for nonblocking module
"""

import sys
if sys.version > '3':
    xrange = range
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest

import os
import time
import tempfile
import shutil
import socket
import errno

#from ioflo.test import testing
from ioflo.base.consoling import getConsole
console = getConsole()

from ioflo.base import nonblocking

def setUpModule():
    console.reinit(verbosity=console.Wordage.concise)

def tearDownModule():
    pass

class BasicTestCase(unittest.TestCase):
    """
    Test Case
    """

    def setUp(self):
        """

        """
        pass

    def tearDown(self):
        """

        """
        pass

    def testConsoleNB(self):
        """
        Test Class ConsoleNB
        """
        console.terse("{0}\n".format(self.testConsoleNB.__doc__))

        myconsole = nonblocking.ConsoleNB()
        result = myconsole.open()
        #self.assertIs(result, False)
        #self.assertIs(result, True)

        #cout = "Enter 'hello' and hit return: "
        #myconsole.put(cout)
        #cin = ''
        #while not cin:
            #cin = myconsole.getLine()
        #myconsole.put("You typed: " + cin)
        #self.assertEqual('hello\n', cin)

        myconsole.close()

    def testSocketUdpNB(self):
        """
        Test Class SocketUdpNb
        """
        console.terse("{0}\n".format(self.testSocketUdpNB.__doc__))
        console.reinit(verbosity=console.Wordage.verbose)
        alpha = nonblocking.SocketUdpNb(port = 6101)
        self.assertIs(alpha.reopen(), True)

        beta = nonblocking.SocketUdpNb(port = 6102)
        self.assertIs(beta.reopen(), True)

        console.terse("Sending alpha to beta\n")
        msgOut = "alpha sends to beta"
        alpha.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])

        console.terse("Sending alpha to alpha\n")
        msgOut = "alpha sends to alpha"
        alpha.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], alpha.ha[1])


        console.terse("Sending beta to alpha\n")
        msgOut = "beta sends to alpha"
        beta.send(msgOut, alpha.ha)
        time.sleep(0.05)
        msgIn, src = alpha.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])


        console.terse("Sending beta to beta\n")
        msgOut = "beta sends to beta"
        beta.send(msgOut, beta.ha)
        time.sleep(0.05)
        msgIn, src = beta.receive()
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src[1], beta.ha[1])

        alpha.close()
        beta.close()
        console.reinit(verbosity=console.Wordage.concise)

    def testSocketUxdNB(self):
        """
        Test Class SocketUxdNb
        """
        console.terse("{0}\n".format(self.testSocketUxdNB.__doc__))
        console.reinit(verbosity=console.Wordage.verbose)

        userDirpath = os.path.join('~', '.ioflo', 'test')
        userDirpath = os.path.abspath(os.path.expanduser(userDirpath))
        if not os.path.exists(userDirpath):
            os.makedirs(userDirpath)

        tempDirpath = tempfile.mkdtemp(prefix="test", suffix="uxd", dir=userDirpath)
        sockDirpath = os.path.join(tempDirpath, 'uxd')
        if not os.path.exists(sockDirpath):
            os.makedirs(sockDirpath)

        ha = os.path.join(sockDirpath, 'alpha.uxd')
        alpha = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = alpha.reopen()
        self.assertIs(result, True)
        self.assertEqual(alpha.ha, ha)

        ha = os.path.join(sockDirpath, 'beta.uxd')
        beta = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = beta.reopen()
        self.assertIs(result, True)
        self.assertEqual(beta.ha, ha)

        ha = os.path.join(sockDirpath, 'gamma.uxd')
        gamma = nonblocking.SocketUxdNb(ha=ha, umask=0x077)
        result = gamma.reopen()
        self.assertIs(result, True)
        self.assertEqual(gamma.ha, ha)

        txMsg = "Alpha sends to Beta"
        alpha.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Alpha sends to Gamma"
        alpha.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Alpha sends to Alpha"
        alpha.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, alpha.ha)

        txMsg = "Beta sends to Alpha"
        beta.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Beta sends to Gamma"
        beta.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Beta sends to Beta"
        beta.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, beta.ha)

        txMsg = "Gamma sends to Alpha"
        gamma.send(txMsg, alpha.ha)
        rxMsg, sa = alpha.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = "Gamma sends to Beta"
        gamma.send(txMsg, beta.ha)
        rxMsg, sa = beta.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)

        txMsg = "Gamma sends to Gamma"
        gamma.send(txMsg, gamma.ha)
        rxMsg, sa = gamma.receive()
        self.assertEqual(txMsg, rxMsg)
        self.assertEqual(sa, gamma.ha)


        pairs = [(alpha, beta), (alpha, gamma), (alpha, alpha),
                 (beta, alpha), (beta, gamma), (beta, beta),
                 (gamma, alpha), (gamma, beta), (gamma, gamma),]
        names = [('alpha', 'beta'), ('alpha', 'gamma'), ('alpha', 'alpha'),
                 ('beta', 'alpha'), ('beta', 'gamma'), ('beta', 'beta'),
                 ('gamma', 'alpha'), ('gamma', 'beta'), ('gamma', 'gamma'),]

        for i, pair in enumerate(pairs):
            txer, rxer = pair
            txName, rxName =  names[i]
            txMsg = "{0} sends to {1} again".format(txName.capitalize(), rxName.capitalize())
            txer.send(txMsg, rxer.ha)
            rxMsg, sa = rxer.receive()
            self.assertEqual(txMsg, rxMsg)
            self.assertEqual(sa, txer.ha)


        rxMsg, sa = alpha.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = beta.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        rxMsg, sa = gamma.receive()
        self.assertIs('', rxMsg)
        self.assertIs(None, sa)

        alpha.close()
        beta.close()
        gamma.close()

        shutil.rmtree(tempDirpath)
        console.reinit(verbosity=console.Wordage.concise)

    def testServerClientSocketTcpNB(self):
        """
        Test Classes ServerSocketTcpNb and ClientSocketTcpNb
        """
        console.terse("{0}\n".format(self.testServerClientSocketTcpNB.__doc__))

        alpha = nonblocking.ServerSocketTcpNb(port = 6101, bufsize=131072)
        self.assertIs(alpha.reopen(), True)
        self.assertEqual(alpha.ha, ('0.0.0.0', 6101))
        alphaHa = ("127.0.0.1", alpha.ha[1])

        beta = nonblocking.ClientSocketTcpNb(ha=alphaHa, bufsize=131072)
        self.assertIs(beta.reopen(), True)

        gamma = nonblocking.ClientSocketTcpNb(ha=alphaHa, bufsize=131072)
        self.assertIs(gamma.reopen(), True)

        console.terse("Connecting beta to alpha\n")
        accepteds = []
        while True:
            if not beta.connected:
                beta.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if beta.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertEqual(len(accepteds), 1)
        csBeta, caBeta = accepteds[0]
        self.assertIsNotNone(csBeta)
        self.assertIsNotNone(caBeta)

        self.assertEqual(csBeta.getsockname(), beta.cs.getpeername())
        self.assertEqual(csBeta.getpeername(), beta.cs.getsockname())
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(caBeta, beta.ca)

        msgOut = "Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, None)

        # send multiple
        msgOut1 = "First Message"
        count = beta.send(msgOut1)
        self.assertEqual(count, len(msgOut1))
        msgOut2 = "Second Message"
        count = beta.send(msgOut2)
        self.assertEqual(count, len(msgOut2))
        time.sleep(0.05)
        msgIn  = alpha.receive(csBeta)
        self.assertEqual(msgIn, msgOut1 + msgOut2)

        # send from alpha to beta
        msgOut = "Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = beta.receive()
        self.assertEqual(msgIn, None)

        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOut = ""
        count = 0
        while (len(msgOut) <= size * 4):
            msgOut += "{0:0>7d} ".format(count)
            count += 1
        self.assertTrue(len(msgOut) >= size * 4)

        msgIn = ''
        count = 0
        while len(msgIn) < len(msgOut):
            if count < len(msgOut):
                count += beta.send(msgOut[count:])
            time.sleep(0.05)
            msgIn += alpha.receive(csBeta)
        self.assertEqual(count, len(msgOut))
        self.assertEqual(msgOut, msgIn)

        console.terse("Connecting gamma to alpha\n")
        accepteds = []
        while True:
            if not gamma.connected:
                gamma.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if gamma.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(gamma.connected, True)
        self.assertEqual(len(accepteds), 1)
        csGamma, caGamma = accepteds[0]
        self.assertIsNotNone(csGamma)
        self.assertIsNotNone(caGamma)

        self.assertEqual(csGamma.getsockname(), gamma.cs.getpeername())
        self.assertEqual(csGamma.getpeername(), gamma.cs.getsockname())
        self.assertEqual(gamma.ca, gamma.cs.getsockname())
        self.assertEqual(gamma.ha, gamma.cs.getpeername())
        self.assertEqual(caGamma, gamma.ca)

        msgOut = "Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgOut, msgIn)

        # receive without sending
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgIn, None)

        # send from alpha to gamma
        msgOut = "Alpha sends to Gamma"
        count = alpha.send(msgOut, csGamma)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)

        # recieve without sending
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)

        # close beta and then attempt to send
        beta.close()
        msgOut = "Send on closed socket"
        with self.assertRaises(AttributeError) as cm:
            count = beta.send(msgOut)

        # attempt to receive on closed socket
        with self.assertRaises(AttributeError) as cm:
            msgIn = beta.receive()

        # read on alpha after closed beta
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, '')

        # send on alpha after close beta
        msgOut = "Alpha sends to Beta after close"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut)) #apparently works

        csBeta.close()

        # send on gamma then shutdown sends
        msgOut = "Gamma sends to Alpha"
        count = gamma.send(msgOut)
        self.assertEqual(count, len(msgOut))
        gamma.shutdownSend()
        time.sleep(0.05)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgOut, msgIn)
        msgIn = alpha.receive(csGamma)
        self.assertEqual(msgIn, '')  # gamma shutdown detected
        # send from alpha to gamma and shutdown
        msgOut = "Alpha sends to Gamma"
        count = alpha.send(msgOut, csGamma)
        self.assertEqual(count, len(msgOut))

        alpha.shutdown(csGamma)  # shutdown alpha
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgOut, msgIn)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)  # alpha shutdown not detected
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, None)  # alpha shutdown not detected

        alpha.shutclose(csGamma)  # close alpha
        time.sleep(0.05)
        msgIn = gamma.receive()
        self.assertEqual(msgIn, '')  # alpha close is detected

        # reopen beta
        self.assertIs(beta.reopen(), True)

        console.terse("Connecting beta to alpha\n")
        accepteds = []
        while True:
            if not beta.connected:
                beta.connect()
            cs, ca = alpha.accept()
            if cs:
                accepteds.append((cs, ca))
            if beta.connected and accepteds:
                break
            time.sleep(0.05)

        self.assertIs(beta.connected, True)
        self.assertEqual(len(accepteds), 1)
        csBeta, caBeta = accepteds[0]
        self.assertIsNotNone(csBeta)
        self.assertIsNotNone(caBeta)

        self.assertEqual(csBeta.getsockname(), beta.cs.getpeername())
        self.assertEqual(csBeta.getpeername(), beta.cs.getsockname())
        self.assertEqual(beta.ca, beta.cs.getsockname())
        self.assertEqual(beta.ha, beta.cs.getpeername())
        self.assertEqual(caBeta, beta.ca)

        msgOut = "Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)

        # send from alpha to beta
        msgOut = "Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut, msgIn)

        # send then shutdown alpha and then attempt to send
        msgOut1 = "Alpha sends to Beta"
        count = alpha.send(msgOut, csBeta)
        self.assertEqual(count, len(msgOut1))
        alpha.shutdownSend(csBeta)
        msgOut2 = "Send on shutdown socket"
        with self.assertRaises(socket.error) as cm:
            count = alpha.send(msgOut, csBeta)
        self.assertTrue(cm.exception.errno == errno.EPIPE)
        time.sleep(0.05)
        msgIn = beta.receive()
        self.assertEqual(msgOut1, msgIn)
        msgIn = beta.receive()
        self.assertEqual(msgIn, '')  # beta detects shutdown socket

        msgOut = "Beta sends to Alpha"
        count = beta.send(msgOut)
        self.assertEqual(count, len(msgOut))
        beta.shutdown()
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgOut, msgIn)
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, None)  # alpha does not detect shutdown
        beta.close()
        time.sleep(0.05)
        msgIn = alpha.receive(csBeta)
        self.assertEqual(msgIn, '')  # alpha detects closed socket

        csBeta.close()

        alpha.close()
        beta.close()
        gamma.close()

    def testSocketTcpNB(self):
        """
        Test Class SocketTcpNb
        """
        console.terse("{0}\n".format(self.testSocketTcpNB.__doc__))

        alpha = nonblocking.SocketTcpNb(port = 6101)
        self.assertIs(alpha.reopen(), True)
        alphaHa = ("127.0.0.1", alpha.ha[1])

        beta = nonblocking.SocketTcpNb(port = 6102)
        self.assertIs(beta.reopen(), True)
        betaHa = ("127.0.0.1", beta.ha[1])

        gamma = nonblocking.SocketTcpNb(port = 6103)
        self.assertIs(gamma.reopen(), True)
        gammaHa = ("127.0.0.1", gamma.ha[1])

        console.terse("Connecting beta to alpha\n")
        result = beta.connect(alphaHa)
        while alphaHa not in beta.peers:
            beta.service()
            alpha.service()

        betaPeerCa, betaPeerCs = beta.peers.items()[0]
        alphaPeerCa, alphaPeerCs = alpha.peers.items()[0]

        self.assertEqual(betaPeerCs.getpeername(), betaPeerCa)
        self.assertEqual(betaPeerCs.getsockname(), alphaPeerCa)
        self.assertEqual(alphaPeerCs.getpeername(), alphaPeerCa)
        self.assertEqual(alphaPeerCs.getsockname(), betaPeerCa)

        msgOut = "beta sends to alpha"
        count = beta.send(msgOut, alphaHa)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        receptions = alpha.receiveAll()
        msgIn, src = receptions[0]
        self.assertEqual(msgOut, msgIn)

        # read without sending
        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, '')
        self.assertEqual(src, None)

        # send multiple
        msgOut1 = "First Message"
        count = beta.send(msgOut1, alphaHa)
        self.assertEqual(count, len(msgOut1))
        msgOut2 = "Second Message"
        count = beta.send(msgOut2, alphaHa)
        self.assertEqual(count, len(msgOut2))
        time.sleep(0.05)
        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, msgOut1 + msgOut2)
        self.assertEqual(src, ca)


        # build message too big to fit in buffer
        sizes = beta.actualBufSizes()
        size = sizes[0]
        msgOut = ""
        count = 0
        while (len(msgOut) <= size * 4):
            msgOut += "{0:0>7d} ".format(count)
            count += 1
        self.assertTrue(len(msgOut) >= size * 4)

        count = 0
        while count < len(msgOut):
            count += beta.send(msgOut[count:], alphaHa)
        self.assertEqual(count, len(msgOut))
        time.sleep(0.05)
        msgIn = ''
        ca, cs = alpha.peers.items()[0]
        count = 0
        while len(msgIn) < len(msgOut):
            rx, src = alpha.receive(ca, bs=len(msgOut))
            count += 1
            msgIn += rx
            time.sleep(0.05)

        self.assertTrue(count > 1)
        self.assertEqual(msgOut, msgIn)
        self.assertEqual(src, ca)

        # Close connection on far side and then read from it near side
        ca, cs = beta.peers.items()[0]
        beta.unconnectPeer(ca)
        self.assertEqual(len(beta.peers), 0)
        time.sleep(0.05)
        msgOut = "Send on unconnected socket"
        with self.assertRaises(ValueError):
            count = beta.send(msgOut, ca)

        #beta.closeshut(cs)
        with self.assertRaises(socket.error) as cm:
            count = cs.send(msgOut)
        self.assertTrue(cm.exception.errno == errno.EBADF)

        ca, cs = alpha.peers.items()[0]
        msgIn, src = alpha.receive(ca)
        self.assertEqual(msgIn, '')
        self.assertEqual(src, ca)  # means closed if empty but ca not None


        #self.assertEqual(src[1], alpha.ha[1])

        #console.terse("Sending alpha to alpha\n")
        #msgOut = "alpha sends to alpha"
        #alpha.send(msgOut, alpha.ha)
        #time.sleep(0.05)
        #msgIn, src = alpha.receive()
        #self.assertEqual(msgOut, msgIn)
        #self.assertEqual(src[1], alpha.ha[1])


        #console.terse("Sending beta to alpha\n")
        #msgOut = "beta sends to alpha"
        #beta.send(msgOut, alpha.ha)
        #time.sleep(0.05)
        #msgIn, src = alpha.receive()
        #self.assertEqual(msgOut, msgIn)
        #self.assertEqual(src[1], beta.ha[1])


        #console.terse("Sending beta to beta\n")
        #msgOut = "beta sends to beta"
        #beta.send(msgOut, beta.ha)
        #time.sleep(0.05)
        #msgIn, src = beta.receive()
        #self.assertEqual(msgOut, msgIn)
        #self.assertEqual(src[1], beta.ha[1])

        alpha.closeAll()
        beta.closeAll()
        gamma.closeAll()


def runOne(test):
    '''
    Unittest Runner
    '''
    test = BasicTestCase(test)
    suite = unittest.TestSuite([test])
    unittest.TextTestRunner(verbosity=2).run(suite)

def runSome():
    """ Unittest runner """
    tests =  []
    names = ['testConsoleNB',
             'testSocketUdpNB',
             'testSocketUxdNB',
             'testSocketTcpNB', ]
    tests.extend(map(BasicTestCase, names))
    suite = unittest.TestSuite(tests)
    unittest.TextTestRunner(verbosity=2).run(suite)

def runAll():
    """ Unittest runner """
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(BasicTestCase))
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__' and __package__ is None:

    #console.reinit(verbosity=console.Wordage.concise)

    #runAll() #run all unittests

    runSome()#only run some

    #runOne('testServerClientSocketTcpNB')

